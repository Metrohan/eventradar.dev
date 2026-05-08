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
