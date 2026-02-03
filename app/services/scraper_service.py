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
        return self.db.query(ScraperLog).order_by(desc(ScraperLog.created_at)).limit(limit).all()

    def get_latest_status(self) -> List[ScraperLog]:
        # Get distinct sources
        sources = self.db.query(ScraperLog.source).distinct().all()
        result = []
        for (source,) in sources:
            latest = self.db.query(ScraperLog).filter(ScraperLog.source == source).order_by(desc(ScraperLog.created_at)).first()
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

    def _run_scraper_task(self, source: str):
        # We need a new session here usually, but for simple logging we can try catch
        # Actually better to invoke the script wrapper that handles DB logging itself?
        # Or we act as the wrapper here.
        # For simplicity, let's call the script via subprocess which is safer for isolation
        
        # Determine script based on source
        script_map = {
            "all": "scripts/run_daily_scrape.py",
            "youthall": "scripts/force_rescrape_youthall.py", # Reusing force script for now or specific
            # Add mapping for others if they have dedicated scripts
        }
        
        target_script = script_map.get(source.lower())
        if not target_script and source.lower() != "all":
             # Try generic match? No, let's stick to 'all' for now or 'youthall'
             pass
        
        if source.lower() == "all":
            cmd = ["python", "scripts/run_daily_scrape.py"]
        elif source.lower() == "youthall":
             # We might want to use the main scraper function directly instead of script
             # But script is easier for now
             cmd = ["python", "-m", "scripts.force_rescrape_youthall"]
        else:
            return # Unknown source

        # Log start?
        
        try:
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True)
            duration = time.time() - start_time
            
            # We need a new DB session since this is a thread
            from ..core.database import SessionLocal
            db = SessionLocal()
            
            status = "success" if result.returncode == 0 else "failed"
            error_msg = result.stderr if result.returncode != 0 else None
            
            # Parse output for events count? Too complex for regex on stdout right now
            # Assume 0 or check logs?
            # Let's just log execution
            
            log = ScraperLog(
                source=source,
                status=status,
                events_found=0, # Placeholder
                new_events=0,   # Placeholder
                error_message=error_msg,
                duration_seconds=duration
            )
            db.add(log)
            db.commit()
            db.close()
            
        except Exception as e:
            # Log failure
            from ..core.database import SessionLocal
            db = SessionLocal()
            log = ScraperLog(
                source=source,
                status="failed",
                error_message=str(e),
                duration_seconds=0
            )
            db.add(log)
            db.commit()
            db.close()


def deactivate_past_events() -> int:
    """Geçmiş etkinlikleri deaktive eder."""
    from ..core.database import SessionLocal
    from ..models.event import Event
    
    db = SessionLocal()
    try:
        now = datetime.now()
        # Tarihi geçmiş ve hala aktif olan etkinlikleri bul
        past_events = db.query(Event).filter(
            Event.is_active == True,
            Event.date < now
        ).all()
        
        count = 0
        for event in past_events:
            event.is_active = False
            count += 1
        
        db.commit()
        return count
    except Exception as e:
        print(f"Error deactivating past events: {e}")
        db.rollback()
        return 0
    finally:
        db.close()

def process_scraped_events(events_data: List[Dict], source_name: str) -> str:
    """Scrape edilen etkinlikleri veritabanına kaydeder."""
    from ..core.database import SessionLocal
    from ..models.event import Event
    from dateparser import parse as parse_date
    
    db = SessionLocal()
    new_count = 0
    updated_count = 0
    
    try:
        for data in events_data:
            url = data.get("url")
            if not url:
                continue
                
            # Date parsing logic
            date_val = data.get("date")
            if isinstance(date_val, str):
                try:
                    # Try parsing with dateparser
                    parsed_dt = parse_date(date_val, languages=["tr"])
                    if parsed_dt:
                        date_val = parsed_dt
                except Exception:
                    pass

            # URL'ye göre mevcut etkinliği ara
            existing_event = db.query(Event).filter(Event.url == url).first()
            
            if existing_event:
                # Güncelle
                existing_event.title = data.get("title", existing_event.title)
                existing_event.description = data.get("description", existing_event.description)
                existing_event.date = date_val if date_val else existing_event.date
                existing_event.location = data.get("location", existing_event.location)
                existing_event.image_url = data.get("image_url", existing_event.image_url)
                existing_event.scraped_at = datetime.now()
                updated_count += 1
            else:
                # Yeni ekle
                new_event = Event(
                    title=data.get("title"),
                    description=data.get("description"),
                    date=date_val,
                    location=data.get("location"),
                    url=url,
                    image_url=data.get("image_url"),
                    source=data.get("source", source_name),
                    is_active=True,
                    scraped_at=datetime.now()
                )
                db.add(new_event)
                new_count += 1
        
        db.commit()
        return f"New: {new_count}, Updated: {updated_count}"
    except Exception as e:
        print(f"Error processing scraped events: {e}")
        db.rollback()
        return f"Error: {str(e)}"
    finally:
        db.close()
