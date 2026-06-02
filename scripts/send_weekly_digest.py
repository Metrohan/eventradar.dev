#!/usr/bin/env python3
"""
Son 7 günde eklenen etkinliklerin özetini Telegram kanalına gönderir.
Etkinlik olmasa bile her Pazartesi gönderilir.
Cron: her Pazartesi 09:00
  0 9 * * 1 cd ~/TechEventRadar && docker compose exec -T backend python scripts/send_weekly_digest.py >> ~/scrape.log 2>&1
"""

import os
import sys
from datetime import datetime, timedelta

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.insert(0, project_root)

from app.core.database import SessionLocal
from app.models.event import Event
from app.services.telegram_service import send_weekly_digest


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
            {"title": e.title, "url": e.url, "source": e.source} for e in events
        ]

        week_label = f"{week_start.strftime('%-d %B')} – {(today - timedelta(days=1)).strftime('%-d %B')}"
        send_weekly_digest(event_dicts, week_label)

        print(f"Haftalık özet gönderildi: {len(event_dicts)} etkinlik ({week_label})")
    finally:
        db.close()


if __name__ == "__main__":
    main()
