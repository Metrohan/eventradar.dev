from unittest.mock import MagicMock
from dataclasses import replace

from app.models.scraper_log import ScraperLog
from app.services.event_ingestion import IngestionResult
from app.services.scrape_run import ScrapeRunCoordinator
from app.services.source_catalog import get_source


def test_run_persists_complete_success_metrics(test_db):
    source = get_source("tech-istanbul")
    assert source is not None
    source = replace(source, runner=lambda: [{"title": "A", "url": "u"}])
    ingestion = MagicMock()
    ingestion.ingest.return_value = IngestionResult(new=1, updated=2)
    ingestion.reconcile_source.return_value = 3
    timer = iter([10.0, 12.5])
    coordinator = ScrapeRunCoordinator(
        lambda: test_db,
        lambda: ingestion,
        timer=lambda: next(timer),
        sleeper=lambda _seconds: None,
    )

    result = coordinator.run(source)

    log = test_db.query(ScraperLog).one()
    assert result.status == "success"
    assert (log.events_found, log.new_events, log.updated_events) == (1, 1, 2)
    assert log.deactivated_events == 3
    assert log.duration_seconds == 2.5


def test_run_failure_does_not_reconcile_and_persists_error(test_db):
    source = get_source("tech-istanbul")
    assert source is not None
    source = replace(source, runner=lambda: (_ for _ in ()).throw(RuntimeError("boom")))
    ingestion = MagicMock()
    timer = iter([10.0, 11.0])
    coordinator = ScrapeRunCoordinator(
        lambda: test_db,
        lambda: ingestion,
        timer=lambda: next(timer),
        sleeper=lambda _seconds: None,
    )

    result = coordinator.run(source)

    assert result.status == "failed"
    assert result.error == "boom"
    assert result.attempts == 3
    ingestion.reconcile_source.assert_not_called()
    assert test_db.query(ScraperLog).one().error_message == "boom"


def test_fetch_retries_with_exponential_backoff_before_ingestion(test_db):
    source = get_source("tech-istanbul")
    assert source is not None
    calls = iter(
        [RuntimeError("one"), RuntimeError("two"), [{"title": "A", "url": "u"}]]
    )

    def flaky_runner():
        value = next(calls)
        if isinstance(value, Exception):
            raise value
        return value

    source = replace(source, runner=flaky_runner)
    ingestion = MagicMock()
    ingestion.ingest.return_value = IngestionResult(new=1)
    ingestion.reconcile_source.return_value = 0
    sleeps = []
    timer = iter([10.0, 13.0])
    coordinator = ScrapeRunCoordinator(
        lambda: test_db,
        lambda: ingestion,
        timer=lambda: next(timer),
        sleeper=sleeps.append,
    )

    result = coordinator.run(source)

    assert result.status == "success"
    assert result.attempts == 3
    assert sleeps == [1.0, 2.0]
    ingestion.ingest.assert_called_once()
    assert test_db.query(ScraperLog).one().attempts == 3
