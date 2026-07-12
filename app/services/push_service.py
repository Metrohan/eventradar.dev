import json
import logging
import os

from pywebpush import WebPushException, webpush
from sqlalchemy.orm import Session

from ..models.push_subscription import PushSubscription

logger = logging.getLogger(__name__)

VAPID_CLAIMS_SUB = "mailto:metehangnn@outlook.com"


def _is_configured() -> bool:
    return bool(os.getenv("VAPID_PRIVATE_KEY") and os.getenv("VAPID_PUBLIC_KEY"))


def _send_to_subscription(sub: PushSubscription, payload: dict) -> bool:
    private_key = os.getenv("VAPID_PRIVATE_KEY", "")
    try:
        webpush(
            subscription_info={
                "endpoint": str(sub.endpoint),
                "keys": {"p256dh": str(sub.p256dh), "auth": str(sub.auth)},
            },
            data=json.dumps(payload),
            vapid_private_key=private_key,
            vapid_claims={"sub": VAPID_CLAIMS_SUB},
        )
        return True
    except WebPushException as exc:
        logger.warning("Push gönderilemedi (endpoint id=%s): %s", sub.id, exc)
        return False


def notify_new_events(db: Session, events: list[dict]) -> None:
    """Yeni etkinlikler için tüm push abonelerine bildirim gönderir.
    Geçersiz/süresi dolmuş abonelikler (410 Gone) veritabanından silinir."""
    if not _is_configured() or not events:
        return

    subscriptions = db.query(PushSubscription).all()
    if not subscriptions:
        return

    event = events[0]
    payload = {
        "title": "Yeni Etkinlik: " + str(event.get("title", "")),
        "body": (
            f"{len(events)} yeni etkinlik eklendi"
            if len(events) > 1
            else str(event.get("source", ""))
        ),
        "url": "https://eventradar.dev",
    }

    stale_ids = []
    for sub in subscriptions:
        try:
            success = _send_to_subscription(sub, payload)
            if not success:
                stale_ids.append(sub.id)
        except Exception as exc:
            logger.error("Push subscription hatası (id=%s): %s", sub.id, exc)

    if stale_ids:
        db.query(PushSubscription).filter(PushSubscription.id.in_(stale_ids)).delete(
            synchronize_session=False
        )
        db.commit()
