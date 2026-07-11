from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
import subprocess
import threading
import time

from ..models.scraper_log import ScraperLog
from ..schemas.scraper_log import ScraperLogCreate
from .event_ingestion import ScrapedEvent, build_event_ingestion
from .source_catalog import get_source


class ScraperService:
    # Tracks source keys (lowercased) with a scrape currently in flight, shared
    # across all instances/threads in this process, guarded by _lock.
    _running_sources: set = set()
    _lock = threading.Lock()

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

        Refuses to start a second run for the same source (or any source while
        "all" is running, and vice versa) so double-clicking "Tetikle" or firing
        overlapping scrapes against the same source can't happen.
        """
        definition = None if source.casefold() == "all" else get_source(source)
        key = definition.key if definition else source.casefold()
        with ScraperService._lock:
            if key in ScraperService._running_sources or (
                "all" in ScraperService._running_sources
            ):
                return {
                    "message": f"{source} için bir tarama zaten çalışıyor, lütfen bekleyin.",
                    "already_running": True,
                }
            if key == "all" and ScraperService._running_sources:
                return {
                    "message": "Başka bir tarama zaten çalışıyor, lütfen bekleyin.",
                    "already_running": True,
                }
            ScraperService._running_sources.add(key)

        target = definition.key if definition else source
        thread = threading.Thread(target=self._run_scraper_task, args=(target,))
        thread.start()
        return {
            "message": f"Scraper {source} triggered locally",
            "already_running": False,
        }

    def _run_scraper_task(self, source: str):
        from ..core.database import SessionLocal

        definition = None if source.casefold() == "all" else get_source(source)
        key = definition.key if definition else source.casefold()
        source_name = definition.name if definition else source
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
            elif definition and definition.enabled:
                events = definition.runner()
                events_found = len(events)
                if events:
                    ingestion = build_event_ingestion()
                    result = ingestion.ingest(
                        ScrapedEvent.from_mapping(event, definition.name)
                        for event in events
                    )
                    new_count = result.new
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
                source=source_name,
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
            with ScraperService._lock:
                ScraperService._running_sources.discard(key)
