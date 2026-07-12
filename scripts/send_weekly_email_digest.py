#!/usr/bin/env python3
"""
Haftalık blog yazısını onaylanmış tüm e-posta abonelerine gönderir.
Yazı henüz üretilmediyse önce idempotent olarak oluşturur.
Cron: her Pazartesi 09:00
  0 9 * * 1 cd ~/TechEventRadar && docker compose exec -T backend python scripts/send_weekly_email_digest.py >> ~/scrape.log 2>&1
"""

import os
import sys
from datetime import datetime

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.insert(0, project_root)

from app.core.database import SessionLocal
from app.models.subscriber import Subscriber
from app.services.email_service import send_weekly_blog_email
from app.services.weekly_content_service import WeeklyContentService


def main() -> None:
    db = SessionLocal()
    try:
        post = WeeklyContentService(db).generate()
        if post.email_sent_at:
            print(f"Bu haftanın blog e-postası daha önce gönderildi: {post.slug}")
            return

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
            ok = send_weekly_blog_email(
                str(subscriber.contact_info),
                str(post.title),
                str(post.summary),
                str(post.content),
                str(post.slug),
                str(subscriber.unsubscribe_token or ""),
            )
            if ok:
                sent += 1
            else:
                failed += 1

        if sent:
            post.email_sent_at = datetime.now()  # type: ignore[assignment]
            db.commit()

        print(f"Haftalık blog e-postası: {sent} gönderildi, {failed} başarısız")
        if failed and not sent:
            sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
