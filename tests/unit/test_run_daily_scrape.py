import os
import sys
from unittest.mock import MagicMock

os.environ.setdefault("ALLOW_INSECURE_DEFAULTS", "true")
os.environ.setdefault("SECRET_KEY", "test-secret-key-that-is-at-least-32-chars")
os.environ.setdefault("ADMIN_USERNAME", "testadmin")
os.environ.setdefault("ADMIN_PASSWORD", "testpassword")

# undetected_chromedriver uses distutils which is removed in Python 3.12+.
# Mock the package before any app imports that trigger it at module level.
_uc_mock = MagicMock()
_uc_mock.ChromeOptions = MagicMock
_uc_mock.Chrome = MagicMock
sys.modules.setdefault("undetected_chromedriver", _uc_mock)

from unittest.mock import patch

from scripts.run_daily_scrape import scrape_source, run_scraper_and_save_to_db
from app.models.scraper_log import ScraperLog


def test_scrape_source_logs_success(test_db):
    def fake_scraper():
        return [{"title": "Event 1"}, {"title": "Event 2"}]

    with patch("app.core.database.SessionLocal", return_value=test_db):
        events = scrape_source(fake_scraper, "Kodluyoruz")

    assert events == [{"title": "Event 1"}, {"title": "Event 2"}]
    log = test_db.query(ScraperLog).filter(ScraperLog.source == "Kodluyoruz").first()
    assert log is not None
    assert log.status == "success"
    assert log.events_found == 2
    assert log.error_message is None


def test_scrape_source_logs_failure(test_db):
    def failing_scraper():
        raise RuntimeError("boom")

    with patch("app.core.database.SessionLocal", return_value=test_db):
        events = scrape_source(failing_scraper, "Youthall")

    assert events == []
    log = test_db.query(ScraperLog).filter(ScraperLog.source == "Youthall").first()
    assert log is not None
    assert log.status == "failed"
    assert log.events_found == 0
    assert "boom" in log.error_message


def test_daily_scrape_deactivates_past_events_after_processing():
    with patch(
        "scripts.run_daily_scrape.deactivate_past_events", side_effect=[0, 2]
    ) as deactivate, patch(
        "scripts.run_daily_scrape.scrape_source",
        return_value=[{"title": "Past", "url": "https://example.com/past"}],
    ), patch(
        "scripts.run_daily_scrape.process_scraped_events", return_value="New: 1"
    ):
        run_scraper_and_save_to_db()

    assert deactivate.call_count == 2
