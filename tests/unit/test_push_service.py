from unittest.mock import MagicMock, patch

from pywebpush import WebPushException

from app.models.push_subscription import PushSubscription
from app.services import push_service


def _subscription() -> PushSubscription:
    subscription = PushSubscription(
        endpoint="https://fcm.googleapis.com/fcm/send/test",
        p256dh="key",
        auth="auth",
    )
    subscription.id = 1
    return subscription


def test_transient_push_failure_does_not_delete_subscription(test_db, monkeypatch):
    subscription = _subscription()
    test_db.add(subscription)
    test_db.commit()
    monkeypatch.setenv("VAPID_PRIVATE_KEY", "private")
    monkeypatch.setenv("VAPID_PUBLIC_KEY", "public")

    with patch.object(push_service, "_send_to_subscription", return_value="failed"):
        push_service.notify_new_events(test_db, [{"title": "Event", "source": "Test"}])

    assert test_db.query(PushSubscription).count() == 1


def test_gone_push_subscription_is_deleted(test_db, monkeypatch):
    subscription = _subscription()
    test_db.add(subscription)
    test_db.commit()
    monkeypatch.setenv("VAPID_PRIVATE_KEY", "private")
    monkeypatch.setenv("VAPID_PUBLIC_KEY", "public")

    with patch.object(push_service, "_send_to_subscription", return_value="stale"):
        push_service.notify_new_events(test_db, [{"title": "Event", "source": "Test"}])

    assert test_db.query(PushSubscription).count() == 0


def test_webpush_410_is_classified_as_stale(monkeypatch):
    monkeypatch.setenv("VAPID_PRIVATE_KEY", "private")
    response = MagicMock(status_code=410)
    error = WebPushException("gone", response=response)

    with patch.object(push_service, "webpush", side_effect=error):
        assert push_service._send_to_subscription(_subscription(), {}) == "stale"
