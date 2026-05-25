#!/usr/bin/env python3
"""One-time script to classify and assign tags to all existing events."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("ALLOW_INSECURE_DEFAULTS", "true")

from app.core.database import SessionLocal
from app.models.event import Event
from app.models.tag import Tag
from app.services.tag_service import classify_event, seed_tags


def backfill():
    db = SessionLocal()
    try:
        seed_tags(db)
        all_tags = {t.name: t for t in db.query(Tag).all()}
        events = db.query(Event).all()
        for event in events:
            tag_names = classify_event(event.title, event.description)
            event.tags = [all_tags[n] for n in tag_names if n in all_tags]
        db.commit()
        print(f"Backfilled {len(events)} events.")
    finally:
        db.close()


if __name__ == "__main__":
    backfill()
