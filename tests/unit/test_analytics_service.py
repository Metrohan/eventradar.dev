import os

os.environ.setdefault("ALLOW_INSECURE_DEFAULTS", "true")
os.environ.setdefault("SECRET_KEY", "test-secret-key-that-is-at-least-32-chars")
os.environ.setdefault("ADMIN_USERNAME", "testadmin")
os.environ.setdefault("ADMIN_PASSWORD", "testpassword")

from app.services.analytics_service import AnalyticsService


def test_get_stats_empty_db_returns_expected_shape(test_db):
    service = AnalyticsService(test_db)
    stats = service.get_stats()
    assert "daily_traffic" in stats
    assert "today_visitors" in stats
    assert "total_visitors" in stats
    assert "top_pages" in stats
    assert isinstance(stats["daily_traffic"], list)
    assert isinstance(stats["top_pages"], list)
    assert stats["today_visitors"] == 0
    assert stats["total_visitors"] == 0


def test_log_request_increments_total(test_db):
    service = AnalyticsService(test_db)
    service.log_request("/api/events", "GET", "127.0.0.1", "pytest-agent")
    service.log_request("/api/events", "GET", "127.0.0.1", "pytest-agent")
    stats = service.get_stats()
    assert stats["total_visitors"] == 2


def test_top_pages_sorted_by_count(test_db):
    service = AnalyticsService(test_db)
    for _ in range(3):
        service.log_request("/api/events", "GET", "1.1.1.1", "ua")
    service.log_request("/api/announcements", "GET", "1.1.1.1", "ua")
    stats = service.get_stats()
    paths = [p["path"] for p in stats["top_pages"]]
    assert paths[0] == "/api/events"
