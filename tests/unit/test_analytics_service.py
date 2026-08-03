import os

os.environ.setdefault("ALLOW_INSECURE_DEFAULTS", "true")
os.environ.setdefault("SECRET_KEY", "test-secret-key-that-is-at-least-32-chars")
os.environ.setdefault("ADMIN_USERNAME", "testadmin")
os.environ.setdefault("ADMIN_PASSWORD", "testpassword")

from datetime import datetime, timedelta

from app.services.analytics_service import AnalyticsService
from app.models.traffic_log import TrafficLog
from sqlalchemy import Text

BINGBOT_USER_AGENT = (
    "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; "
    "bingbot/2.0; +http://www.bing.com/bingbot.htm) Chrome/136.0.0.0 "
    "Safari/537.36 AppleWebKit/537.36 (KHTML, like Gecko; compatible; "
    "bingbot/2.0; +http://www.bing.com/bingbot.htm) Chrome/116.0.1938.76 "
    "Safari/537.36"
)


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


def test_log_request_accepts_long_bingbot_user_agent(test_db):
    assert len(BINGBOT_USER_AGENT) == 273
    assert isinstance(TrafficLog.__table__.c.user_agent.type, Text)

    service = AnalyticsService(test_db)
    service.log_request("/api/events", "GET", "172.18.0.1", BINGBOT_USER_AGENT)

    log = test_db.query(TrafficLog).one()
    assert log.user_agent == BINGBOT_USER_AGENT


def test_top_pages_sorted_by_count(test_db):
    service = AnalyticsService(test_db)
    for _ in range(3):
        service.log_request("/api/events", "GET", "1.1.1.1", "ua")
    service.log_request("/api/announcements", "GET", "1.1.1.1", "ua")
    stats = service.get_stats()
    paths = [p["path"] for p in stats["top_pages"]]
    assert paths[0] == "/api/events"


def test_today_visitors_excludes_yesterday(test_db):
    yesterday = datetime.now() - timedelta(days=1)
    test_db.add_all(
        [
            TrafficLog(
                path="/api/events",
                method="GET",
                ip_address="1.1.1.1",
                user_agent="ua",
                timestamp=yesterday,
            ),
            TrafficLog(
                path="/api/events",
                method="GET",
                ip_address="1.1.1.1",
                user_agent="ua",
                timestamp=yesterday,
            ),
            TrafficLog(
                path="/api/events", method="GET", ip_address="1.1.1.1", user_agent="ua"
            ),
        ]
    )
    test_db.commit()

    stats = AnalyticsService(test_db).get_stats()

    assert stats["total_visitors"] == 3
    assert stats["today_visitors"] == 1


def test_top_pages_tie_both_paths_present(test_db):
    # Two paths with equal request counts — tie-break order is DB-specific
    # (SQLite returns rows in group-by scan order; no guarantee on which comes first).
    # Assert presence and correct counts; do not assert relative order of tied entries.
    test_db.add_all(
        [
            TrafficLog(
                path="/api/events", method="GET", ip_address="1.1.1.1", user_agent="ua"
            ),
            TrafficLog(
                path="/api/events", method="GET", ip_address="1.1.1.1", user_agent="ua"
            ),
            TrafficLog(
                path="/api/announcements",
                method="GET",
                ip_address="1.1.1.1",
                user_agent="ua",
            ),
            TrafficLog(
                path="/api/announcements",
                method="GET",
                ip_address="1.1.1.1",
                user_agent="ua",
            ),
        ]
    )
    test_db.commit()

    stats = AnalyticsService(test_db).get_stats()
    by_path = {p["path"]: p["count"] for p in stats["top_pages"]}

    assert "/api/events" in by_path
    assert "/api/announcements" in by_path
    assert by_path["/api/events"] == 2
    assert by_path["/api/announcements"] == 2
