from datetime import datetime, timedelta

from app.models.event import Event
from app.models.scraper_log import ScraperLog
from app.services.source_quality import SourceQuality


def test_source_quality_reports_completeness_and_run_health(test_db):
    now = datetime.now()
    test_db.add_all(
        [
            Event(
                title="Complete",
                description="Description",
                date=now,
                location="Online",
                url="https://example.com/complete",
                source="Tech Istanbul",
                is_active=True,
                scraped_at=now,
                last_seen_at=now,
            ),
            Event(
                title="Incomplete",
                url="https://example.com/incomplete",
                source="Tech Istanbul",
                is_active=False,
                scraped_at=now,
                last_seen_at=now,
            ),
            ScraperLog(
                source="Tech Istanbul",
                status="failed",
                error_message="timeout",
                created_at=now,
            ),
            ScraperLog(
                source="Tech Istanbul",
                status="success",
                created_at=now - timedelta(days=1),
            ),
        ]
    )
    test_db.commit()

    metrics = SourceQuality(test_db).get_metrics()
    tech_istanbul = next(item for item in metrics if item["key"] == "tech-istanbul")

    assert tech_istanbul["total_events"] == 2
    assert tech_istanbul["active_events"] == 1
    assert tech_istanbul["missing_date"] == 1
    assert tech_istanbul["missing_location"] == 1
    assert tech_istanbul["missing_description"] == 1
    assert tech_istanbul["completeness_percent"] == 50.0
    assert tech_istanbul["success_rate_percent"] == 50.0
    assert tech_istanbul["consecutive_failures"] == 1
    assert tech_istanbul["last_error"] == "timeout"
