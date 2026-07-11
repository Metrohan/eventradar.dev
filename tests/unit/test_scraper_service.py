import os

os.environ.setdefault("ALLOW_INSECURE_DEFAULTS", "true")
os.environ.setdefault("SECRET_KEY", "test-secret-key-that-is-at-least-32-chars")
os.environ.setdefault("ADMIN_USERNAME", "testadmin")
os.environ.setdefault("ADMIN_PASSWORD", "testpassword")

from unittest.mock import patch
import pytest
from app.services.scraper_service import ScraperService


@pytest.fixture(autouse=True)
def _clear_running_sources():
    ScraperService._running_sources.clear()
    yield
    ScraperService._running_sources.clear()


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
