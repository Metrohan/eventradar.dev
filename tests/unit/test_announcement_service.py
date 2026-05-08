import os

os.environ.setdefault("ALLOW_INSECURE_DEFAULTS", "true")
os.environ.setdefault("SECRET_KEY", "test-secret-key-that-is-at-least-32-chars")
os.environ.setdefault("ADMIN_USERNAME", "testadmin")
os.environ.setdefault("ADMIN_PASSWORD", "testpassword")

from app.services.announcement_service import AnnouncementService
from app.schemas.announcement import AnnouncementCreate


def test_create_and_get_announcement(test_db):
    service = AnnouncementService(test_db)
    created = service.create_announcement(
        AnnouncementCreate(title="Hello", message="World")
    )
    assert created.id is not None
    assert created.title == "Hello"
    assert created.message == "World"


def test_get_announcements_returns_list(test_db):
    service = AnnouncementService(test_db)
    service.create_announcement(AnnouncementCreate(title="A", message="msg"))
    service.create_announcement(AnnouncementCreate(title="B", message="msg"))
    items = service.get_announcements()
    assert len(items) == 2


def test_get_announcement_by_id(test_db):
    service = AnnouncementService(test_db)
    created = service.create_announcement(AnnouncementCreate(title="X", message="Y"))
    fetched = service.get_announcement_by_id(created.id)
    assert fetched is not None
    assert fetched.id == created.id


def test_get_announcement_by_id_not_found(test_db):
    service = AnnouncementService(test_db)
    assert service.get_announcement_by_id(9999) is None


def test_get_latest_announcement(test_db):
    service = AnnouncementService(test_db)
    service.create_announcement(AnnouncementCreate(title="First", message="m"))
    service.create_announcement(AnnouncementCreate(title="Second", message="m"))
    latest = service.get_latest_announcement()
    assert latest is not None


def test_delete_announcement(test_db):
    service = AnnouncementService(test_db)
    created = service.create_announcement(AnnouncementCreate(title="Del", message="m"))
    assert service.delete_announcement(created.id) is True
    assert service.get_announcement_by_id(created.id) is None


def test_delete_announcement_not_found(test_db):
    service = AnnouncementService(test_db)
    assert service.delete_announcement(9999) is False
