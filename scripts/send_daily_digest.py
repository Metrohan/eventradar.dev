#!/usr/bin/env python3
"""
Bir önceki günde eklenen etkinliklerin özetini Telegram kanalına gönderir.
Cron: her sabah 09:00
  0 9 * * * cd ~/TechEventRadar && docker compose exec -T backend python scripts/send_daily_digest.py >> ~/scrape.log 2>&1
"""

import os
import sys
from datetime import datetime, timedelta

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.insert(0, project_root)

from app.core.database import SessionLocal
from app.models.event import Event
from app.services.telegram_service import send_daily_digest


def main() -> None:
    db = SessionLocal()
    try:
        yesterday_start = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        ) - timedelta(days=1)
        yesterday_end = yesterday_start + timedelta(days=1)

        events = (
            db.query(Event)
            .filter(
                Event.is_active == True,
                Event.scraped_at >= yesterday_start,
                Event.scraped_at < yesterday_end,
            )
            .order_by(Event.scraped_at.desc())
            .all()
        )

        event_dicts = [
            {"title": e.title, "url": e.url, "source": e.source} for e in events
        ]

        date_label = yesterday_start.strftime("%-d %B %Y")

        if not event_dicts:
            print(f"Günlük özet atlandı: dün ({date_label}) yeni etkinlik yok")
            return

        sent = send_daily_digest(event_dicts, date_label)
        if sent:
            print(f"Günlük özet gönderildi: {len(event_dicts)} etkinlik ({date_label})")
        else:
            print(
                "Günlük özet GÖNDERİLEMEDİ (TELEGRAM_BOT_TOKEN/TELEGRAM_CHANNEL_ID "
                "eksik olabilir veya Telegram API hatası oluştu — loglara bakın)."
            )
            sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
