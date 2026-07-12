import os
import sys
from unittest.mock import MagicMock, patch

os.environ.setdefault("ALLOW_INSECURE_DEFAULTS", "true")
os.environ.setdefault("SECRET_KEY", "test-secret-key-that-is-at-least-32-chars")
os.environ.setdefault("ADMIN_USERNAME", "testadmin")
os.environ.setdefault("ADMIN_PASSWORD", "testpassword")

_uc_mock = MagicMock()
_uc_mock.ChromeOptions = MagicMock
_uc_mock.Chrome = MagicMock
sys.modules.setdefault("undetected_chromedriver", _uc_mock)

from app.services.scrape_run import ScrapeRunResult
from scripts.run_daily_scrape import run_scraper_and_save_to_db


def test_daily_scrape_uses_coordinator_and_cleans_past_events():
    ingestion = MagicMock()
    ingestion.deactivate_past.side_effect = [0, 2]
    coordinator = MagicMock()
    coordinator.run_all.return_value = [
        ScrapeRunResult(source="Tech Istanbul", status="success", fetched=2, new=1)
    ]

    with patch(
        "scripts.run_daily_scrape.build_event_ingestion", return_value=ingestion
    ), patch(
        "scripts.run_daily_scrape.build_scrape_run_coordinator",
        return_value=coordinator,
    ):
        run_scraper_and_save_to_db()

    coordinator.run_all.assert_called_once_with()
    assert ingestion.deactivate_past.call_count == 2
