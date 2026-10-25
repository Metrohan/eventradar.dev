import logging
from sqlalchemy.orm import Session
from sqlalchemy import or_
from ..models.subscriber import Subscriber
from ..schemas.subscriber import BroadcastRequest
from ..core.config import settings
from typing import List
import requests as http_requests
from . import email_service

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self, db: Session):
        self.db = db

    def get_subscribers(self) -> List[Subscriber]:
        return self.db.query(Subscriber).all()

    def get_stats(self):
        total = self.db.query(Subscriber).count()
        telegram = (
            self.db.query(Subscriber).filter(Subscriber.channel == "telegram").count()
        )
        email = self.db.query(Subscriber).filter(Subscriber.channel == "email").count()
        active = self.db.query(Subscriber).filter(Subscriber.is_active == True).count()
        return {
            "total_subscribers": total,
            "telegram_count": telegram,
            "email_count": email,
            "active_count": active,
        }

    def broadcast_message(self, request: BroadcastRequest) -> dict:
        query = self.db.query(Subscriber).filter(
            Subscriber.is_active == True,
            or_(Subscriber.channel != "email", Subscriber.confirmed.is_(True)),
        )
        if request.target_channel != "all":
            query = query.filter(Subscriber.channel == request.target_channel)
        subscribers = query.all()

        sent = 0
        failed = 0
        for sub in subscribers:
            if request.target_interest and request.target_interest not in (
                sub.interests or []
            ):
                continue
            try:
                if sub.channel == "email":
                    self._send_email(
                        str(sub.contact_info),
                        "EventRadar Bildirimi",
                        request.message,
                        unsubscribe_token=(
                            str(sub.unsubscribe_token)
                            if sub.unsubscribe_token is not None
                            else None
                        ),
                    )
                elif sub.channel == "telegram":
                    self._send_telegram(str(sub.contact_info), request.message)
                sent += 1
            except Exception as e:
                logger.error("Notification failed for %s: %s", sub.contact_info, e)
                failed += 1

        return {
            "status": "success",
            "message": f"Message sent to {sent} subscribers",
            "recipient_count": sent,
            "failed_count": failed,
        }

    def _send_email(
        self, to: str, subject: str, body: str, unsubscribe_token: str | None = None
    ) -> None:
        if not email_service.send_plain_email(to, subject, body, unsubscribe_token):
            raise RuntimeError("Email delivery failed or SMTP is not configured")

    def _send_telegram(self, chat_id: str, message: str) -> None:
        if settings.debug or not settings.telegram_bot_token:
            logger.info("[DEV] Telegram to %s: %s", chat_id, message)
            return

        url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
        resp = http_requests.post(
            url, json={"chat_id": chat_id, "text": message}, timeout=10
        )
        resp.raise_for_status()
