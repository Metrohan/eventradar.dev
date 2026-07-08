import os

os.environ.setdefault("ALLOW_INSECURE_DEFAULTS", "true")
os.environ.setdefault("SECRET_KEY", "test-secret-key-that-is-at-least-32-chars")
os.environ.setdefault("ADMIN_USERNAME", "testadmin")
os.environ.setdefault("ADMIN_PASSWORD", "testpassword")

from datetime import datetime, timedelta
from unittest.mock import patch
import pytest
from app.services.scraper_service import (
    ScraperService,
    normalize_date,
    deactivate_past_events,
)
from app.models.event import Event


@pytest.fixture(autouse=True)
def _clear_running_sources():
    ScraperService._running_sources.clear()
    yield
    ScraperService._running_sources.clear()


def test_normalize_date_none():
    assert normalize_date(None) is None


def test_normalize_date_empty_string():
    assert normalize_date("") is None


def test_normalize_date_datetime_passthrough():
    dt = datetime(2027, 5, 15)
    assert normalize_date(dt) == dt


def test_normalize_date_invalid_text():
    assert normalize_date("tarih belirtilmemiş") is None
    assert normalize_date("-") is None


def test_normalize_date_valid_turkish_string():
    result = normalize_date("15 Mayıs 2027")
    assert isinstance(result, datetime)
    assert result.month == 5


def test_deactivate_past_events(test_db):
    past = Event(
        title="Past Event",
        url="https://example.com/past",
        source="test",
        is_active=True,
        date=datetime.now() - timedelta(days=2),
        scraped_at=datetime.now(),
    )
    future = Event(
        title="Future Event",
        url="https://example.com/future",
        source="test",
        is_active=True,
        date=datetime.now() + timedelta(days=2),
        scraped_at=datetime.now(),
    )
    test_db.add_all([past, future])
    test_db.commit()

    past_id = past.id
    future_id = future.id

    # Patch definition-site because deactivate_past_events uses a local import
    # (`from ..core.database import SessionLocal` inside the function body),
    # so patching the module-level name is the only way to intercept it.
    with patch("app.core.database.SessionLocal", return_value=test_db):
        count = deactivate_past_events()

    assert count == 1
    from app.models.event import Event as EventModel

    past_after = test_db.query(EventModel).filter(EventModel.id == past_id).first()
    future_after = test_db.query(EventModel).filter(EventModel.id == future_id).first()
    assert past_after.is_active is False
    assert future_after.is_active is True


def test_trigger_scraper_refuses_when_source_already_running(test_db):
    service = ScraperService(test_db)
    ScraperService._running_sources.add("youthall")

    with patch.object(ScraperService, "_run_scraper_task") as mock_run:
        result = service.trigger_scraper("Youthall")

    mock_run.assert_not_called()
    assert result["already_running"] is True


def test_trigger_scraper_refuses_when_all_is_running(test_db):
    service = ScraperService(test_db)
    ScraperService._running_sources.add("all")

    with patch.object(ScraperService, "_run_scraper_task") as mock_run:
        result = service.trigger_scraper("Kodluyoruz")

    mock_run.assert_not_called()
    assert result["already_running"] is True


def test_trigger_scraper_starts_when_nothing_running(test_db):
    service = ScraperService(test_db)

    with patch("threading.Thread") as mock_thread_cls:
        mock_thread = mock_thread_cls.return_value
        result = service.trigger_scraper("Youthall")

    mock_thread.start.assert_called_once()
    assert result["already_running"] is False
    assert "youthall" in ScraperService._running_sources
