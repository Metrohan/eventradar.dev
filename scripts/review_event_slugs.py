"""Create a clean-route preview; apply/rollback only the exact reviewed snapshot."""

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.database import SessionLocal
from app.models.event import Event, EventSlugAlias
from app.utils.event_urls import slug_base


def fingerprint(event):
    return hashlib.sha256(
        json.dumps(
            [event.url, event.title, str(event.date)], ensure_ascii=False
        ).encode()
    ).hexdigest()


def plan_slugs(events, aliases):
    owners = {alias.slug: alias.event_id for alias in aliases}
    for event in events:
        if event.slug in owners and owners[event.slug] != event.id:
            raise ValueError("Existing route namespace collision")
        owners[event.slug] = event.id
    changes = []
    for event in sorted(events, key=lambda row: row.id):
        if event.slug_version != 1:
            continue
        base = slug_base(event.title, event.date)
        candidate = base
        number = 1
        while candidate in owners and owners[candidate] != event.id:
            number += 1
            candidate = f"{base}-{number}"
        owners[candidate] = event.id
        if candidate != event.slug or event.slug_version == 1:
            changes.append(
                dict(
                    id=event.id,
                    old=event.slug,
                    new=candidate,
                    content_hash=fingerprint(event),
                    old_version=event.slug_version,
                    new_version=2,
                )
            )
    return changes


def apply_routes(db, changes, rollback=False):
    rows = {
        e.id: e
        for e in db.query(Event)
        .filter(Event.id.in_([c["id"] for c in changes]))
        .with_for_update()
        .all()
    }
    for change in changes:
        event = rows.get(change["id"])
        before = change["new"] if rollback else change["old"]
        after = change["old"] if rollback else change["new"]
        owner = db.query(EventSlugAlias).filter_by(slug=after).first()
        if (
            event is None
            or event.slug != before
            or event.slug_version
            != (change["new_version"] if rollback else change["old_version"])
            or fingerprint(event) != change["content_hash"]
            or (owner is not None and owner.event_id != event.id)
        ):
            raise ValueError("Route snapshot changed; create a new preview")
    for change in changes:
        rows[change["id"]].slug = change["old"] if rollback else change["new"]
        rows[change["id"]].slug_version = (
            change["old_version"] if rollback else change["new_version"]
        )
    db.commit()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--apply", action="store_true")
    modes.add_argument("--rollback", action="store_true")
    parser.add_argument("--expected-plan-sha")
    args = parser.parse_args()
    db = SessionLocal()
    try:
        if args.apply or args.rollback:
            raw = args.plan.read_bytes()
            if (
                not args.expected_plan_sha
                or hashlib.sha256(raw).hexdigest() != args.expected_plan_sha
            ):
                raise ValueError("Exact reviewed plan SHA required")
            apply_routes(db, json.loads(raw), rollback=args.rollback)
            print("Restored" if args.rollback else "Applied")
        else:
            changes = plan_slugs(db.query(Event).all(), db.query(EventSlugAlias).all())
            raw = (json.dumps(changes, ensure_ascii=False, indent=2) + "\n").encode()
            with args.plan.open("xb") as out:
                out.write(raw)
            print(
                json.dumps(
                    dict(changes=len(changes), plan_sha=hashlib.sha256(raw).hexdigest())
                )
            )
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
