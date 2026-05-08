import os

os.environ.setdefault("ALLOW_INSECURE_DEFAULTS", "true")
os.environ.setdefault("SECRET_KEY", "test-secret-key-that-is-at-least-32-chars")
os.environ.setdefault("ADMIN_USERNAME", "testadmin")
os.environ.setdefault("ADMIN_PASSWORD", "testpassword")

import pytest
from app.services.event_service import EventService
from app.schemas.event import EventCreate, EventUpdate


def _create_data(**kwargs) -> EventCreate:
    defaults = dict(
        title="Python Bootcamp Istanbul",
        description="A great bootcamp",
        url="https://example.com/event",
        source="test",
        is_active=True,
    )
    defaults.update(kwargs)
    return EventCreate(**defaults)


def test_create_and_get_event(test_db):
    service = EventService(test_db)
    event = service.create_event(_create_data())
    assert event.id is not None
    assert event.title == "Python Bootcamp Istanbul"
    assert event.source == "test"


def test_get_event_by_id(test_db):
    service = EventService(test_db)
    created = service.create_event(_create_data())
    fetched = service.get_event_by_id(created.id)
    assert fetched is not None
    assert fetched.id == created.id


def test_get_event_by_id_not_found(test_db):
    service = EventService(test_db)
    assert service.get_event_by_id(9999) is None


def test_get_events_active_only(test_db):
    service = EventService(test_db)
    service.create_event(_create_data(url="https://example.com/a", is_active=True))
    service.create_event(_create_data(url="https://example.com/b", is_active=False))
    active = service.get_events(active_only=True)
    assert len(active) == 1
    assert all(e.is_active for e in active)


def test_get_events_all(test_db):
    service = EventService(test_db)
    service.create_event(_create_data(url="https://example.com/a", is_active=True))
    service.create_event(_create_data(url="https://example.com/b", is_active=False))
    all_events = service.get_events(active_only=False)
    assert len(all_events) == 2


def test_update_event_title(test_db):
    service = EventService(test_db)
    created = service.create_event(_create_data())
    updated = service.update_event(created.id, EventUpdate(title="New Title"))
    assert updated is not None
    assert updated.title == "New Title"


def test_update_event_not_found_returns_none(test_db):
    service = EventService(test_db)
    result = service.update_event(9999, EventUpdate(title="X"))
    assert result is None


def test_delete_event(test_db):
    service = EventService(test_db)
    created = service.create_event(_create_data())
    assert service.delete_event(created.id) is True
    assert service.get_event_by_id(created.id) is None


def test_delete_event_not_found(test_db):
    service = EventService(test_db)
    assert service.delete_event(9999) is False


def test_duplicate_url_raises(test_db):
    service = EventService(test_db)
    service.create_event(_create_data())
    with pytest.raises(ValueError, match="already exists"):
        service.create_event(_create_data())


def test_get_total_active_events(test_db):
    service = EventService(test_db)
    service.create_event(_create_data(url="https://example.com/a", is_active=True))
    service.create_event(_create_data(url="https://example.com/b", is_active=False))
    assert service.get_total_active_events() == 1


def test_get_last_updated_event(test_db):
    service = EventService(test_db)
    service.create_event(_create_data())
    latest = service.get_last_updated_event()
    assert latest is not None
