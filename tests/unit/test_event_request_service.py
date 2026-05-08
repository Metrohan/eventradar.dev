import os

os.environ.setdefault("ALLOW_INSECURE_DEFAULTS", "true")
os.environ.setdefault("SECRET_KEY", "test-secret-key-that-is-at-least-32-chars")
os.environ.setdefault("ADMIN_USERNAME", "testadmin")
os.environ.setdefault("ADMIN_PASSWORD", "testpassword")

import pytest
from app.services.event_request_service import EventRequestService
from app.schemas.event_request import EventRequestCreate


def _req(**kwargs) -> EventRequestCreate:
    defaults = dict(
        event_link="https://example.com/event",
        event_title="Cool Hackathon",
    )
    defaults.update(kwargs)
    return EventRequestCreate(**defaults)


def test_create_and_get_event_request(test_db):
    service = EventRequestService(test_db)
    created = service.create_event_request(_req())
    assert created.id is not None
    assert created.event_title == "Cool Hackathon"


def test_get_event_requests_returns_list(test_db):
    service = EventRequestService(test_db)
    service.create_event_request(_req(event_link="https://example.com/a"))
    service.create_event_request(_req(event_link="https://example.com/b"))
    items = service.get_event_requests()
    assert len(items) == 2


def test_get_event_request_by_id(test_db):
    service = EventRequestService(test_db)
    created = service.create_event_request(_req())
    fetched = service.get_event_request_by_id(created.id)
    assert fetched is not None
    assert fetched.id == created.id


def test_get_event_request_by_id_not_found(test_db):
    service = EventRequestService(test_db)
    assert service.get_event_request_by_id(9999) is None


def test_delete_event_request(test_db):
    service = EventRequestService(test_db)
    created = service.create_event_request(_req())
    assert service.delete_event_request(created.id) is True
    assert service.get_event_request_by_id(created.id) is None


def test_delete_event_request_not_found(test_db):
    service = EventRequestService(test_db)
    assert service.delete_event_request(9999) is False
