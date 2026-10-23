import pytest
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


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("203.0.113.57", "203.0.113.0"),
        ("::ffff:203.0.113.57", "203.0.113.0"),
        ("2001:db8:abcd:1234:5678:9abc:def0:1234", "2001:db8:abcd::"),
        ("not-an-ip", None),
        ("", None),
        (None, None),
    ],
)
def test_anonymize_ip(raw, expected):
    from app.services.analytics_service import anonymize_ip

    assert anonymize_ip(raw) == expected


def test_log_request_stores_only_truncated_ip(test_db):
    AnalyticsService(test_db).log_request("/api/events", "GET", "203.0.113.57", "ua")
    assert test_db.query(TrafficLog).one().ip_address == "203.0.113.0"


def test_purge_removes_only_rows_older_than_retention(test_db):
    old = datetime.now() - timedelta(days=91)
    recent = datetime.now() - timedelta(days=89)
    test_db.add_all(
        [
            TrafficLog(path="/old", method="GET", timestamp=old),
            TrafficLog(path="/recent", method="GET", timestamp=recent),
        ]
    )
    test_db.commit()
    assert AnalyticsService(test_db).purge_old_logs() == 1
    assert [row.path for row in test_db.query(TrafficLog).all()] == ["/recent"]


def test_log_request_triggers_daily_purge_once(test_db, monkeypatch):
    from app.services import analytics_service

    monkeypatch.setattr(analytics_service, "_last_purge", float("-inf"))
    test_db.add(
        TrafficLog(
            path="/old", method="GET", timestamp=datetime.now() - timedelta(days=200)
        )
    )
    test_db.commit()
    service = AnalyticsService(test_db)
    service.log_request("/new", "GET", "198.51.100.9", "ua")
    assert [row.path for row in test_db.query(TrafficLog).all()] == ["/new"]
    # second call within the interval must not purge again
    test_db.add(
        TrafficLog(
            path="/old2", method="GET", timestamp=datetime.now() - timedelta(days=200)
        )
    )
    test_db.commit()
    service.log_request("/new2", "GET", "198.51.100.9", "ua")
    assert "/old2" in [row.path for row in test_db.query(TrafficLog).all()]
