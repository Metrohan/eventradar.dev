import os

os.environ.setdefault("ALLOW_INSECURE_DEFAULTS", "true")
os.environ.setdefault("SECRET_KEY", "test-secret-key-that-is-at-least-32-chars")
os.environ.setdefault("ADMIN_USERNAME", "testadmin")
os.environ.setdefault("ADMIN_PASSWORD", "testpassword")

import pytest
from app.models.event import Event
from app.models.announcement import Announcement
from datetime import datetime


def _seed_event(db, url="https://example.com/ev"):
    e = Event(
        title="Admin Event",
        url=url,
        source="test",
        is_active=True,
        scraped_at=datetime.now(),
    )
    db.add(e)
    db.commit()
    db.refresh(e)
    return e


# ── auth ──────────────────────────────────────────────────────────────────────


def test_login_success(client):
    resp = client.post(
        "/api/admin/login",
        json={"username": "testadmin", "password": "testpassword"},
    )
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_wrong_password(client):
    resp = client.post(
        "/api/admin/login",
        json={"username": "testadmin", "password": "wrong"},
    )
    assert resp.status_code == 401


# ── protected endpoints require auth ─────────────────────────────────────────


def test_get_admin_events_requires_auth(client):
    resp = client.get("/api/admin/events")
    assert resp.status_code == 401


def test_create_event_requires_auth(client):
    resp = client.post("/api/admin/events", json={})
    assert resp.status_code == 401


# ── event CRUD ────────────────────────────────────────────────────────────────


def test_get_admin_events_with_auth(client, auth_headers):
    resp = client.get("/api/admin/events", headers=auth_headers)
    assert resp.status_code == 200
    assert "events" in resp.json()


def test_create_event_with_auth(client, auth_headers):
    payload = {
        "title": "New Admin Event",
        "url": "https://example.com/new",
        "source": "admin",
        "is_active": True,
    }
    resp = client.post("/api/admin/events", json=payload, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["title"] == "New Admin Event"


def test_update_event_with_auth(client, auth_headers, test_db):
    event = _seed_event(test_db)
    resp = client.put(
        f"/api/admin/events/{event.id}",
        json={"title": "Updated Title"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "Updated Title"


def test_delete_event_with_auth(client, auth_headers, test_db):
    event = _seed_event(test_db)
    resp = client.delete(f"/api/admin/events/{event.id}", headers=auth_headers)
    assert resp.status_code == 200


def test_delete_event_not_found(client, auth_headers):
    resp = client.delete("/api/admin/events/99999", headers=auth_headers)
    assert resp.status_code == 404


# ── announcements ─────────────────────────────────────────────────────────────


def test_create_announcement_with_auth(client, auth_headers):
    payload = {"title": "System Notice", "message": "Maintenance tonight."}
    resp = client.post("/api/admin/announcements", json=payload, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["title"] == "System Notice"


def test_delete_announcement_with_auth(client, auth_headers, test_db):
    a = Announcement(title="To Delete", message="bye")
    test_db.add(a)
    test_db.commit()
    test_db.refresh(a)
    resp = client.delete(f"/api/admin/announcements/{a.id}", headers=auth_headers)
    assert resp.status_code == 200


def test_delete_announcement_not_found(client, auth_headers):
    resp = client.delete("/api/admin/announcements/99999", headers=auth_headers)
    assert resp.status_code == 404


# ── notifications ────────────────────────────────────────────────────────────


def test_broadcast_rejects_empty_message(client, auth_headers):
    resp = client.post(
        "/api/admin/notifications/broadcast",
        json={"message": "", "target_channel": "all"},
        headers=auth_headers,
    )
    assert resp.status_code == 422


def test_broadcast_rejects_too_short_message(client, auth_headers):
    resp = client.post(
        "/api/admin/notifications/broadcast",
        json={"message": "short", "target_channel": "all"},
        headers=auth_headers,
    )
    assert resp.status_code == 422


def test_broadcast_accepts_valid_message(client, auth_headers):
    resp = client.post(
        "/api/admin/notifications/broadcast",
        json={"message": "This is a valid broadcast message.", "target_channel": "all"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["recipient_count"] == 0
