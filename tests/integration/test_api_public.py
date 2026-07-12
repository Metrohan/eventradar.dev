import os

os.environ.setdefault("ALLOW_INSECURE_DEFAULTS", "true")
os.environ.setdefault("SECRET_KEY", "test-secret-key-that-is-at-least-32-chars")
os.environ.setdefault("ADMIN_USERNAME", "testadmin")
os.environ.setdefault("ADMIN_PASSWORD", "testpassword")

import pytest
from unittest.mock import patch
from app.models.event import Event
from app.models.announcement import Announcement
from datetime import datetime, timedelta


def _seed_event(db, url="https://example.com/ev", is_active=True):
    e = Event(
        title="Test Event",
        url=url,
        source="test",
        is_active=is_active,
        scraped_at=datetime.now(),
    )
    db.add(e)
    db.commit()
    db.refresh(e)
    return e


def _seed_announcement(db, title="Notice", message="Hello"):
    a = Announcement(title=title, message=message)
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


# ── /health ───────────────────────────────────────────────────────────────────


def test_health_check(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


# ── /api/events ───────────────────────────────────────────────────────────────


def test_get_events_empty(client):
    resp = client.get("/api/events")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_count"] == 0
    assert data["events"] == []


def test_get_events_returns_active_events(client, test_db):
    _seed_event(test_db, url="https://example.com/a", is_active=True)
    _seed_event(test_db, url="https://example.com/b", is_active=False)
    resp = client.get("/api/events?active_only=true")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_count"] == 1
    assert len(data["events"]) == 1


def test_get_events_all_when_active_only_false(client, test_db):
    _seed_event(test_db, url="https://example.com/a", is_active=True)
    _seed_event(test_db, url="https://example.com/b", is_active=False)
    resp = client.get("/api/events?active_only=false")
    assert resp.status_code == 200
    assert len(resp.json()["events"]) == 2
    assert resp.json()["total_count"] == 2


def test_get_events_paginates_without_changing_total_count(client, test_db):
    for index in range(3):
        _seed_event(test_db, url=f"https://example.com/page-{index}", is_active=True)

    first = client.get("/api/events?page=1&page_size=2")
    second = client.get("/api/events?page=2&page_size=2")

    assert first.status_code == 200
    assert len(first.json()["events"]) == 2
    assert len(second.json()["events"]) == 1
    assert first.json()["total_count"] == 3
    assert first.json()["total_pages"] == 2
    assert first.json()["page"] == 1


def test_get_events_rejects_invalid_pagination(client):
    assert client.get("/api/events?page=0").status_code == 422
    assert client.get("/api/events?page_size=201").status_code == 422


def test_events_rss_returns_well_formed_feed_with_expected_items(client, test_db):
    import xml.etree.ElementTree as ET

    for index in range(3):
        _seed_event(test_db, url=f"https://example.com/rss-{index}", is_active=True)

    response = client.get("/api/events/rss")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/rss+xml")

    root = ET.fromstring(response.text)
    assert root.tag == "rss"
    channel = root.find("channel")
    assert channel is not None
    items = channel.findall("item")
    assert len(items) == 3
    for item in items:
        assert item.find("title") is not None
        assert item.find("link") is not None
        assert item.find("pubDate") is not None


def test_events_rss_excludes_inactive_events(client, test_db):
    import xml.etree.ElementTree as ET

    _seed_event(test_db, url="https://example.com/rss-active", is_active=True)
    _seed_event(test_db, url="https://example.com/rss-inactive", is_active=False)

    response = client.get("/api/events/rss")
    root = ET.fromstring(response.text)
    items = root.find("channel").findall("item")

    assert len(items) == 1


def test_get_event_detail_hides_inactive_event(client, test_db):
    event = _seed_event(test_db, is_active=False)

    resp = client.get(f"/api/events/{event.id}")

    assert resp.status_code == 404


def test_get_event_detail_hides_past_event_even_if_flag_is_active(client, test_db):
    event = _seed_event(test_db, is_active=True)
    event.date = datetime.now() - timedelta(days=1)
    test_db.commit()

    resp = client.get(f"/api/events/{event.id}")

    assert resp.status_code == 404


def test_get_event_detail_returns_active_future_event(client, test_db):
    event = _seed_event(test_db, is_active=True)
    event.date = datetime.now() + timedelta(days=1)
    test_db.commit()

    resp = client.get(f"/api/events/{event.id}")

    assert resp.status_code == 200
    assert resp.json()["id"] == event.id


def test_get_sources_returns_enabled_catalog_without_runners(client):
    resp = client.get("/api/sources")

    assert resp.status_code == 200
    sources = resp.json()
    assert len(sources) == 8
    assert any(source["key"] == "tech-istanbul" for source in sources)
    assert all(source["enabled"] is True for source in sources)
    assert all("runner" not in source for source in sources)


# ── /api/announcements ────────────────────────────────────────────────────────


def test_get_announcements_empty(client):
    resp = client.get("/api/announcements")
    assert resp.status_code == 200
    assert resp.json()["total_count"] == 0


def test_get_announcements_returns_items(client, test_db):
    _seed_announcement(test_db, title="First")
    _seed_announcement(test_db, title="Second")
    resp = client.get("/api/announcements")
    assert resp.status_code == 200
    assert resp.json()["total_count"] == 2


def test_get_latest_announcement_none(client):
    resp = client.get("/api/announcements/latest")
    assert resp.status_code == 200
    assert resp.json() is None


def test_get_latest_announcement_returns_item(client, test_db):
    _seed_announcement(test_db, title="Latest")
    resp = client.get("/api/announcements/latest")
    assert resp.status_code == 200
    assert resp.json()["title"] == "Latest"


def test_get_latest_announcement_reports_service_failure(client):
    with patch(
        "app.services.announcement_service.AnnouncementService.get_latest_announcement",
        side_effect=RuntimeError("database unavailable"),
    ):
        resp = client.get("/api/announcements/latest")

    assert resp.status_code == 500
    assert resp.json()["detail"] == "Duyuru yüklenirken bir hata oluştu"
    assert "database unavailable" not in resp.text


# ── /api/suggestions ─────────────────────────────────────────────────────────


def test_post_suggestion(client):
    payload = {
        "suggestion_type": "oneri",
        "suggestion_title": "Better UI",
        "suggestion_text": "Please improve the mobile UI",
    }
    resp = client.post("/api/suggestions", json=payload)
    assert resp.status_code == 200
    assert resp.json()["suggestion_title"] == "Better UI"


@pytest.mark.parametrize(
    "payload",
    [
        {"suggestion_type": "x", "suggestion_title": "OK", "suggestion_text": "short"},
        {
            "suggestion_type": "oneri",
            "suggestion_title": "   ",
            "suggestion_text": "A valid long message",
        },
        {
            "suggestion_type": "oneri",
            "suggestion_title": "Valid",
            "suggestion_text": "x" * 5001,
        },
    ],
)
def test_post_suggestion_rejects_invalid_content(client, payload):
    assert client.post("/api/suggestions", json=payload).status_code == 422


def test_public_forms_are_rate_limited(client):
    from app.api.public import public_form_limiter

    public_form_limiter.reset()
    payload = {
        "suggestion_type": "oneri",
        "suggestion_title": "Rate limit",
        "suggestion_text": "This is a valid suggestion message.",
    }
    headers = {"x-forwarded-for": "203.0.113.50"}

    for _ in range(5):
        assert (
            client.post("/api/suggestions", json=payload, headers=headers).status_code
            == 200
        )
    blocked = client.post("/api/suggestions", json=payload, headers=headers)

    assert blocked.status_code == 429
    assert blocked.headers["retry-after"]
    public_form_limiter.reset()


# ── /api/event-requests ───────────────────────────────────────────────────────


def test_post_event_request(client):
    payload = {
        "event_link": "https://example.com/hackathon",
        "event_title": "Global Hackathon",
    }
    resp = client.post("/api/event-requests", json=payload)
    assert resp.status_code == 200
    assert resp.json()["event_title"] == "Global Hackathon"


@pytest.mark.parametrize(
    "payload",
    [
        {"event_link": "javascript:alert(1)", "event_title": "Valid Event"},
        {"event_link": "https://example.com", "event_title": "  "},
        {
            "event_link": "https://example.com",
            "event_title": "Valid",
            "contact_email": "not-an-email",
        },
        {
            "event_link": "https://example.com",
            "event_title": "Valid",
            "event_description": "x" * 5001,
        },
    ],
)
def test_post_event_request_rejects_invalid_content(client, payload):
    assert client.post("/api/event-requests", json=payload).status_code == 422


from app.services.tag_service import seed_tags
from app.models.tag import Tag as TagModel
from app.models.event import Event as EventModel


def _seed_event_with_title(db, url, title):
    e = EventModel(
        title=title, url=url, source="test", is_active=True, scraped_at=datetime.now()
    )
    db.add(e)
    db.commit()
    db.refresh(e)
    return e


def test_get_events_tags_in_response(client, test_db):
    seed_tags(test_db)
    tags = {t.name: t for t in test_db.query(TagModel).all()}
    event = _seed_event(test_db)
    event.tags = [tags["hackathon"]]
    test_db.commit()

    resp = client.get("/api/events")
    assert resp.status_code == 200
    events = resp.json()["events"]
    assert len(events) == 1
    assert events[0]["tags"] == ["hackathon"]


def test_get_events_filter_by_tags(client, test_db):
    seed_tags(test_db)
    tags = {t.name: t for t in test_db.query(TagModel).all()}
    e1 = _seed_event_with_title(
        test_db, url="https://example.com/hack", title="Hackathon 2026"
    )
    e2 = _seed_event_with_title(
        test_db, url="https://example.com/work", title="Workshop"
    )
    e1.tags = [tags["hackathon"]]
    e2.tags = [tags["atolye"]]
    test_db.commit()

    resp = client.get("/api/events?tags=hackathon")
    assert resp.status_code == 200
    events = resp.json()["events"]
    assert len(events) == 1
    assert events[0]["tags"] == ["hackathon"]
