from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Dict, Optional
import subprocess
import threading
from datetime import datetime
import time

from ..models.scraper_log import ScraperLog
from ..schemas.scraper_log import ScraperLogCreate


class ScraperService:
    def __init__(self, db: Session):
        self.db = db

    def create_log(self, log_data: ScraperLogCreate) -> ScraperLog:
        db_log = ScraperLog(**log_data.dict())
        self.db.add(db_log)
        self.db.commit()
        self.db.refresh(db_log)
        return db_log

    def get_logs(self, limit: int = 50) -> List[ScraperLog]:
        return (
            self.db.query(ScraperLog)
            .order_by(desc(ScraperLog.created_at))
            .limit(limit)
            .all()
        )

    def get_latest_status(self) -> List[ScraperLog]:
        # Get distinct sources
        sources = self.db.query(ScraperLog.source).distinct().all()
        result = []
        for (source,) in sources:
            latest = (
                self.db.query(ScraperLog)
                .filter(ScraperLog.source == source)
                .order_by(desc(ScraperLog.created_at))
                .first()
            )
            if latest:
                result.append(latest)
        return result

    def trigger_scraper(self, source: str):
        """
        Triggers a scraper in a separate thread.
        This is a simplified implementation. in prod usually task queue (celery) is used.
        """
        thread = threading.Thread(target=self._run_scraper_task, args=(source,))
        thread.start()
        return {"message": f"Scraper {source} triggered locally"}

    # Kaynak adı → scraper fonksiyonu eşlemesi
    SCRAPER_FUNCS = {
        "techcareer.net": "app.scrapers.techcareer_scraper:scrape_techcareer_events",
        "coderspace": "app.scrapers.cs_scraper:scrape_coderspace_events",
        "anbean": "app.scrapers.anbean_scraper:scrape_anbean_events",
        "kodluyoruz": "app.scrapers.kodluyoruz_scraper:scrape_kodluyoruz_events",
        "youthall": "app.scrapers.youthall_scraper:scrape_youthall_events",
        "akbank gençlik akademisi": "app.scrapers.akbank_scraper:scrape_akbank_events",
        "pupilica": "app.scrapers.pupilica_scraper:scrape_pupilica_events",
    }

    def _run_scraper_task(self, source: str):
        from ..core.database import SessionLocal
        import importlib

        key = source.lower()
        status = "failed"
        error_msg = None
        events_found = 0
        new_count = 0

        start_time = time.time()
        try:
            if key == "all":
                # Tüm scraper'ları sırayla çalıştır
                cmd = ["python", "scripts/run_daily_scrape.py"]
                proc = subprocess.run(cmd, capture_output=True, text=True)
                status = "success" if proc.returncode == 0 else "failed"
                if proc.returncode != 0:
                    error_msg = proc.stderr
            elif key in self.SCRAPER_FUNCS:
                # İlgili scraper fonksiyonunu dinamik olarak çağır
                module_path, func_name = self.SCRAPER_FUNCS[key].rsplit(":", 1)
                module = importlib.import_module(module_path)
                scraper_func = getattr(module, func_name)
                events = scraper_func()
                events_found = len(events)
                if events:
                    result_str = process_scraped_events(events, source)
                    try:
                        new_count = int(
                            result_str.split("New:")[1].split(",")[0].strip()
                        )
                    except Exception:
                        pass
                status = "success"
            else:
                error_msg = f"Bilinmeyen kaynak: {source}"
                status = "failed"
        except Exception as e:
            error_msg = str(e)
            status = "failed"

        duration = time.time() - start_time
        db = SessionLocal()
        try:
            log = ScraperLog(
                source=source,
                status=status,
                events_found=events_found,
                new_events=new_count,
                error_message=error_msg,
                duration_seconds=duration,
            )
            db.add(log)
            db.commit()
        finally:
            db.close()


def deactivate_past_events() -> int:
    """Geçmiş etkinlikleri deaktive eder."""
    from ..core.database import SessionLocal
    from ..models.event import Event

    db = SessionLocal()
    try:
        now = datetime.now()
        # Tarihi geçmiş ve hala aktif olan etkinlikleri bul
        past_events = (
            db.query(Event).filter(Event.is_active == True, Event.date < now).all()
        )

        count = 0
        for event in past_events:
            event.is_active = False  # type: ignore[assignment]
            count += 1

        db.commit()
        return count
    except Exception as e:
        print(f"Error deactivating past events: {e}")
        db.rollback()
        return 0
    finally:
        db.close()


def normalize_date(date_val) -> Optional[datetime]:
    from app.services.date_extractor import parse_event_date

    if not date_val:
        return None
    if isinstance(date_val, datetime):
        return date_val
    if isinstance(date_val, str):
        # Ortak geçersiz metinler kontrolü
        invalid_texts = ["tarih belirtilmemiş", "belirtilmemiş", "-", ""]
        if date_val.strip().lower() in invalid_texts:
            return None
        return parse_event_date(date_val)
    return None


def process_scraped_events(events_data: List[Dict], source_name: str) -> str:
    """Scrape edilen etkinlikleri veritabanına kaydeder."""
    from ..core.database import SessionLocal
    from ..models.event import Event
    from ..models.tag import Tag
    from .tag_service import classify_event

    db = SessionLocal()
    new_count = 0
    updated_count = 0
    failed_urls = []

    try:
        urls = [d.get("url") for d in events_data if d.get("url")]
        existing_map = {
            e.url: e for e in db.query(Event).filter(Event.url.in_(urls)).all()
        }
        all_tags: dict[str, Tag] = {str(t.name): t for t in db.query(Tag).all()}

        now = datetime.now()
        seen_urls: set[str] = set()
        new_event_data: list[dict] = []
        for data in events_data:
            url = data.get("url")
            if not url or url in seen_urls:
                continue
            seen_urls.add(url)
            try:
                date_val = normalize_date(data.get("date"))
                existing_event = existing_map.get(url)

                if existing_event:
                    existing_event.title = data.get("title", existing_event.title)
                    existing_event.description = data.get(
                        "description", existing_event.description
                    )
                    if date_val is not None:
                        existing_event.date = date_val  # type: ignore[assignment]
                    existing_event.location = data.get(
                        "location", existing_event.location
                    )
                    existing_event.image_url = data.get(
                        "image_url", existing_event.image_url
                    )
                    existing_event.scraped_at = now  # type: ignore[assignment]
                    tag_names = classify_event(
                        data.get("title", existing_event.title),
                        data.get("description", existing_event.description),
                    )
                    existing_event.tags = [
                        all_tags[n] for n in tag_names if n in all_tags
                    ]
                    updated_count += 1
                else:
                    new_event = Event(
                        title=data.get("title"),
                        description=data.get("description"),
                        date=date_val,
                        location=data.get("location"),
                        url=url,
                        image_url=data.get("image_url"),
                        source=data.get("source", source_name),
                        is_active=True,
                        scraped_at=now,
                    )
                    db.add(new_event)
                    db.flush()
                    tag_names = classify_event(
                        data.get("title", ""), data.get("description")
                    )
                    new_event.tags = [all_tags[n] for n in tag_names if n in all_tags]
                    new_count += 1
                    new_event_data.append(data)
            except Exception as e_event:
                print(f"Error processing single event ({url}): {e_event}")
                failed_urls.append(url)
                continue

        db.commit()

        if new_event_data:
            try:
                from .telegram_service import notify_new_events

                notify_new_events(new_event_data)
            except Exception as tg_err:
                print(f"Telegram bildirimi gönderilemedi (non-fatal): {tg_err}")

        result = f"New: {new_count}, Updated: {updated_count}"
        if failed_urls:
            result += f", Failed: {len(failed_urls)}"
        return result
    except Exception as e:
        db.rollback()
        print(f"Error in process_scraped_events: {e}")
        return f"Error: {str(e)}"
    finally:
        db.close()
