import os

os.environ.setdefault("ALLOW_INSECURE_DEFAULTS", "true")
os.environ.setdefault("SECRET_KEY", "test-secret-key-that-is-at-least-32-chars")
os.environ.setdefault("ADMIN_USERNAME", "testadmin")
os.environ.setdefault("ADMIN_PASSWORD", "testpassword")

import pytest
from unittest.mock import patch, MagicMock
from app.services.notification_service import NotificationService
from app.models.subscriber import Subscriber
from app.schemas.subscriber import BroadcastRequest


def _make_subscriber(channel: str, contact: str, active: bool = True) -> Subscriber:
    s = Subscriber()
    s.channel = channel
    s.contact_info = contact
    s.is_active = active
    s.interests = []
    return s


def test_get_stats_empty_db(test_db):
    service = NotificationService(test_db)
    stats = service.get_stats()
    assert stats["total_subscribers"] == 0
    assert stats["telegram_count"] == 0
    assert stats["email_count"] == 0
    assert stats["active_count"] == 0


def test_get_stats_with_subscribers(test_db):
    test_db.add_all(
        [
            _make_subscriber("email", "a@example.com"),
            _make_subscriber("telegram", "123456"),
            _make_subscriber("email", "b@example.com", active=False),
        ]
    )
    test_db.commit()

    service = NotificationService(test_db)
    stats = service.get_stats()
    assert stats["total_subscribers"] == 3
    assert stats["email_count"] == 2
    assert stats["telegram_count"] == 1
    assert stats["active_count"] == 2


def test_broadcast_email_calls_send_email(test_db):
    test_db.add(_make_subscriber("email", "test@example.com"))
    test_db.commit()

    service = NotificationService(test_db)
    with patch.object(service, "_send_email") as mock_send:
        req = BroadcastRequest(message="Hello there!", target_channel="email")
        result = service.broadcast_message(req)

    mock_send.assert_called_once_with(
        "test@example.com",
        "EventRadar Bildirimi",
        "Hello there!",
        unsubscribe_token=None,
    )
    assert result["recipient_count"] == 1
    assert result["failed_count"] == 0


def test_broadcast_telegram_calls_send_telegram(test_db):
    test_db.add(_make_subscriber("telegram", "987654"))
    test_db.commit()

    service = NotificationService(test_db)
    with patch.object(service, "_send_telegram") as mock_send:
        req = BroadcastRequest(message="Hello there!", target_channel="telegram")
        result = service.broadcast_message(req)

    mock_send.assert_called_once_with("987654", "Hello there!")
    assert result["recipient_count"] == 1


def test_broadcast_failed_subscriber_counted(test_db):
    test_db.add(_make_subscriber("email", "bad@example.com"))
    test_db.commit()

    service = NotificationService(test_db)
    with patch.object(service, "_send_email", side_effect=Exception("SMTP error")):
        req = BroadcastRequest(message="Hello there!", target_channel="all")
        result = service.broadcast_message(req)

    assert result["failed_count"] == 1
    assert result["recipient_count"] == 0
