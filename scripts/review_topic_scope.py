"""Preview/apply/rollback an evidence-bound topic scope plan; no messages or deletes."""

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import or_
from app.core.database import SessionLocal
from app.models.event import Event
from app.services.topic_policy import classify_event
from app.utils.event_dates import day_start


def content_hash(event):
    values = [event.url, event.title, event.description, str(event.date), event.source]
    return hashlib.sha256(json.dumps(values, ensure_ascii=False).encode()).hexdigest()


def plan_changes(events):
    changes = []
    for event in events:
        if not event.is_active and event.deactivation_reason not in ("topic", "past"):
            continue
        decision = classify_event(event.title, event.description, event.source)
        allowed = decision.allowed
        before = [bool(event.is_active), event.deactivation_reason]
        if not allowed:
            after = [False, "topic"]
        elif event.deactivation_reason == "topic":
            active = event.date is None or event.date >= day_start()
            after = [active, None if active else "past"]
        else:
            after = before
        if after != before:
            changes.append(
                dict(
                    id=event.id,
                    url=event.url,
                    title=event.title,
                    reason=f"{decision.tier}: {decision.reason}",
                    content_hash=content_hash(event),
                    before=before,
                    after=after,
                )
            )
    return sorted(changes, key=lambda row: row["id"])


def apply_plan(db, changes, rollback=False):
    rows = {
        event.id: event
        for event in db.query(Event)
        .filter(Event.id.in_([c["id"] for c in changes]))
        .with_for_update()
        .all()
    }
    # Validate the complete plan before changing anything. A newer scrape or a
    # manual edit invalidates the snapshot and requires another preview.
    for change in changes:
        row = rows.get(change["id"])
        expected = change["after"] if rollback else change["before"]
        if (
            row is None
            or row.url != change["url"]
            or content_hash(row) != change["content_hash"]
            or [bool(row.is_active), row.deactivation_reason] != expected
        ):
            raise ValueError("Plan snapshot changed; no writes applied")
    for change in changes:
        row = rows[change["id"]]
        row.is_active, row.deactivation_reason = (
            change["before"] if rollback else change["after"]
        )
    db.commit()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--rollback", action="store_true")
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
            apply_plan(db, json.loads(raw), rollback=args.rollback)
            print("Restored" if args.rollback else "Applied")
        else:
            events = (
                db.query(Event)
                .filter(
                    or_(
                        Event.is_active.is_(True),
                        Event.deactivation_reason.in_(("topic", "past")),
                    )
                )
                .all()
            )
            changes = plan_changes(events)
            raw = (json.dumps(changes, ensure_ascii=False, indent=2) + "\n").encode()
            # The plan is also the rollback record. Never overwrite an existing plan.
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
