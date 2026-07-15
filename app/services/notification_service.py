import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate, make_msgid, parseaddr
from sqlalchemy.orm import Session
from ..models.subscriber import Subscriber
from ..schemas.subscriber import BroadcastRequest
from ..core.config import settings
from typing import List
import requests as http_requests

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
        query = self.db.query(Subscriber).filter(Subscriber.is_active == True)
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
                        unsubscribe_token=sub.unsubscribe_token,
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
        if settings.debug or not settings.smtp_host:
            logger.info("[DEV] Email to %s: %s", to, body)
            return

        from_addr = settings.smtp_from
        _, from_email = parseaddr(from_addr)
        domain = from_email.split("@")[-1] if "@" in from_email else "eventradar.dev"

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = from_addr
        msg["To"] = to
        msg["Date"] = formatdate(localtime=True)
        msg["Message-ID"] = make_msgid(domain=domain)
        if unsubscribe_token:
            unsubscribe_url = (
                f"https://eventradar.dev/abone-iptal?token={unsubscribe_token}"
            )
            msg["List-Unsubscribe"] = f"<{unsubscribe_url}>"
            body = f"{body}\n\nAbonelikten çık: {unsubscribe_url}"
        msg.attach(MIMEText(body, "plain", "utf-8"))

        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_pass)
            server.sendmail(from_email, to, msg.as_string())

    def _send_telegram(self, chat_id: str, message: str) -> None:
        if settings.debug or not settings.telegram_bot_token:
            logger.info("[DEV] Telegram to %s: %s", chat_id, message)
            return

        url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
        resp = http_requests.post(
            url, json={"chat_id": chat_id, "text": message}, timeout=10
        )
        resp.raise_for_status()
