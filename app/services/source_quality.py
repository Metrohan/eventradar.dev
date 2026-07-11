from dataclasses import asdict, dataclass

from sqlalchemy.orm import Session

from ..models.event import Event
from ..models.scraper_log import ScraperLog
from .source_catalog import get_enabled_sources


@dataclass(frozen=True)
class SourceQualityMetric:
    key: str
    source: str
    total_events: int
    active_events: int
    missing_date: int
    missing_location: int
    missing_description: int
    completeness_percent: float
    success_rate_percent: float | None
    consecutive_failures: int
    last_status: str | None
    last_error: str | None
    last_run_at: str | None


class SourceQuality:
    """Compute source health and event-data completeness behind one interface."""

    def __init__(self, db: Session):
        self._db = db

    def get_metrics(self, run_window: int = 20) -> list[dict]:
        return [
            asdict(self._metric_for(source.key, source.name, run_window))
            for source in get_enabled_sources()
        ]

    def _metric_for(
        self, key: str, source_name: str, run_window: int
    ) -> SourceQualityMetric:
        events = self._db.query(Event).filter(Event.source == source_name).all()
        logs = (
            self._db.query(ScraperLog)
            .filter(ScraperLog.source == source_name)
            .order_by(ScraperLog.created_at.desc())
            .limit(run_window)
            .all()
        )

        total = len(events)
        missing_date = sum(event.date is None for event in events)
        missing_location = sum(not event.location for event in events)
        missing_description = sum(not event.description for event in events)
        field_total = total * 3
        completeness = (
            round(
                100
                * (field_total - missing_date - missing_location - missing_description)
                / field_total,
                1,
            )
            if field_total
            else 100.0
        )
        success_rate = (
            round(100 * sum(log.status == "success" for log in logs) / len(logs), 1)
            if logs
            else None
        )
        consecutive_failures = 0
        for log in logs:
            if log.status != "failed":
                break
            consecutive_failures += 1

        latest = logs[0] if logs else None
        return SourceQualityMetric(
            key=key,
            source=source_name,
            total_events=total,
            active_events=sum(bool(event.is_active) for event in events),
            missing_date=missing_date,
            missing_location=missing_location,
            missing_description=missing_description,
            completeness_percent=completeness,
            success_rate_percent=success_rate,
            consecutive_failures=consecutive_failures,
            last_status=str(latest.status) if latest else None,
            last_error=(
                str(latest.error_message) if latest and latest.error_message else None
            ),
            last_run_at=(
                latest.created_at.isoformat() if latest and latest.created_at else None
            ),
        )
