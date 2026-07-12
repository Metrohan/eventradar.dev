#!/usr/bin/env python3
"""
Son 7 günde eklenen etkinliklerin özetini onaylanmış tüm e-posta
abonelerine gönderir.
Cron: her Pazartesi 09:00
  0 9 * * 1 cd ~/TechEventRadar && docker compose exec -T backend python scripts/send_weekly_email_digest.py >> ~/scrape.log 2>&1
"""

import os
import sys
from datetime import datetime, timedelta

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.insert(0, project_root)

from app.core.database import SessionLocal
from app.models.event import Event
from app.models.subscriber import Subscriber
from app.services.email_service import send_weekly_digest_email


def main() -> None:
    db = SessionLocal()
    try:
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today - timedelta(days=7)

        events = (
            db.query(Event)
            .filter(
                Event.is_active == True,
                Event.scraped_at >= week_start,
                Event.scraped_at < today,
            )
            .order_by(Event.scraped_at.desc())
            .all()
        )
        event_dicts = [
            {"id": e.id, "title": e.title, "source": e.source} for e in events
        ]

        subscribers = (
            db.query(Subscriber)
            .filter(
                Subscriber.channel == "email",
                Subscriber.confirmed == True,
                Subscriber.is_active == True,
            )
            .all()
        )

        if not subscribers:
            print("Gönderilecek onaylı abone yok.")
            return

        sent, failed = 0, 0
        for subscriber in subscribers:
            ok = send_weekly_digest_email(
                str(subscriber.contact_info),
                event_dicts,
                str(subscriber.unsubscribe_token or ""),
            )
            if ok:
                sent += 1
            else:
                failed += 1

        print(f"Haftalık e-posta özeti: {sent} gönderildi, {failed} başarısız")
        if failed and not sent:
            sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
