from dataclasses import dataclass
from time import monotonic, sleep
from typing import Callable, Literal

from sqlalchemy.orm import Session

from ..models.scraper_log import ScraperLog
from .event_ingestion import EventIngestion, ScrapedEvent
from .source_catalog import SourceDefinition, get_enabled_sources

RunStatus = Literal["success", "failed"]


@dataclass(frozen=True)
class ScrapeRunResult:
    source: str
    status: RunStatus
    fetched: int = 0
    new: int = 0
    updated: int = 0
    failed: int = 0
    deactivated: int = 0
    duration_seconds: float = 0.0
    error: str | None = None
    attempts: int = 1


class ScrapeRunCoordinator:
    """Run, ingest, reconcile, and persist one consistent source outcome."""

    def __init__(
        self,
        session_factory: Callable[[], Session],
        ingestion_factory: Callable[[], EventIngestion],
        timer: Callable[[], float] = monotonic,
        sleeper: Callable[[float], None] = sleep,
        max_fetch_attempts: int = 3,
        backoff_seconds: float = 1.0,
    ):
        self._session_factory = session_factory
        self._ingestion_factory = ingestion_factory
        self._timer = timer
        self._sleeper = sleeper
        self._max_fetch_attempts = max_fetch_attempts
        self._backoff_seconds = backoff_seconds

    def run(self, source: SourceDefinition) -> ScrapeRunResult:
        started = self._timer()
        attempts = 0
        try:
            events, attempts = self._fetch_with_retry(source)
            ingestion = self._ingestion_factory()
            ingestion_result = ingestion.ingest(
                ScrapedEvent.from_mapping(event, source.name) for event in events
            )
            deactivated = ingestion.reconcile_source(source.name)
            result = ScrapeRunResult(
                source=source.name,
                status="success",
                fetched=len(events),
                new=ingestion_result.new,
                updated=ingestion_result.updated,
                failed=ingestion_result.failed,
                deactivated=deactivated,
                duration_seconds=self._timer() - started,
                attempts=attempts,
            )
        except Exception as exc:
            result = ScrapeRunResult(
                source=source.name,
                status="failed",
                duration_seconds=self._timer() - started,
                error=str(exc),
                attempts=attempts or self._max_fetch_attempts,
            )

        self._persist(result)
        return result

    def run_all(self) -> list[ScrapeRunResult]:
        return [self.run(source) for source in get_enabled_sources()]

    def _fetch_with_retry(self, source: SourceDefinition) -> tuple[list[dict], int]:
        for attempt in range(1, self._max_fetch_attempts + 1):
            try:
                return source.runner(), attempt
            except Exception:
                if attempt == self._max_fetch_attempts:
                    raise
                self._sleeper(self._backoff_seconds * (2 ** (attempt - 1)))
        raise RuntimeError("unreachable")

    def _persist(self, result: ScrapeRunResult) -> None:
        db = self._session_factory()
        try:
            db.add(
                ScraperLog(
                    source=result.source,
                    status=result.status,
                    events_found=result.fetched,
                    new_events=result.new,
                    updated_events=result.updated,
                    deactivated_events=result.deactivated,
                    failed_events=result.failed,
                    error_message=result.error,
                    duration_seconds=result.duration_seconds,
                    attempts=result.attempts,
                )
            )
            db.commit()
        finally:
            db.close()


def build_scrape_run_coordinator() -> ScrapeRunCoordinator:
    from ..core.database import SessionLocal
    from .event_ingestion import build_event_ingestion

    return ScrapeRunCoordinator(SessionLocal, build_event_ingestion)
