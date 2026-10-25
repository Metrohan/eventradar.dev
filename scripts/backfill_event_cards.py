"""ADR-0006 migration: regenerate cards for all events and archive old thumbnails.

Dry-run (default):   python scripts/backfill_event_cards.py
Apply (after DB dump): python scripts/backfill_event_cards.py --apply --archive-dir /path/outside/served/dir
"""

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))

from app.core.config import settings
from app.core.database import SessionLocal
from app.services.card_backfill import backfill_cards


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    parser.add_argument("--archive-dir", type=Path, help="where orphan files are moved")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        report = backfill_cards(
            db,
            Path(settings.thumbnail_dir),
            settings.thumbnail_public_prefix,
            archive_dir=args.archive_dir,
            apply=args.apply,
        )
    finally:
        db.close()

    mode = "APPLIED" if args.apply else "DRY-RUN (nothing changed)"
    print(f"{mode}")
    print(
        f"events: {report.events_total}, rows to change: {report.rows_to_change}, "
        f"rows without a card: {report.rows_without_card}"
    )
    print(f"orphan thumbnail files: {len(report.orphan_files)}")
    for f in report.orphan_files[:10]:
        print(f"  {f.name}")
    if report.archived_to:
        print(f"moved to: {report.archived_to}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
