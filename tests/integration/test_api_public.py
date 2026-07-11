import os

os.environ.setdefault("ALLOW_INSECURE_DEFAULTS", "true")
os.environ.setdefault("SECRET_KEY", "test-secret-key-that-is-at-least-32-chars")
os.environ.setdefault("ADMIN_USERNAME", "testadmin")
os.environ.setdefault("ADMIN_PASSWORD", "testpassword")

import pytest
from app.models.event import Event
from app.models.announcement import Announcement
from datetime import datetime


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


# ── /api/event-requests ───────────────────────────────────────────────────────


def test_post_event_request(client):
    payload = {
        "event_link": "https://example.com/hackathon",
        "event_title": "Global Hackathon",
    }
    resp = client.post("/api/event-requests", json=payload)
    assert resp.status_code == 200
    assert resp.json()["event_title"] == "Global Hackathon"


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
