"""Stable clean canonicals and a shared reservation namespace for old routes."""

import re
import unicodedata
from datetime import datetime

from sqlalchemy import insert
from sqlalchemy.exc import IntegrityError


def slug_base(title, date=None):
    text = str(title or "etkinlik").translate(
        str.maketrans("ıİşŞğĞüÜöÖçÇ", "iIsSgGuUoOcC")
    )
    text = (
        unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    )
    base = re.sub(r"[^a-z0-9]+", "-", text).strip("-")[:100].rstrip("-") or "etkinlik"
    if isinstance(date, datetime):
        base += "-" + date.strftime("%Y-%m-%d")
    return base


def new_event_slug(context):
    from ..models.event import EventSlugAlias

    params = context.get_current_parameters()
    base = slug_base(params.get("title"), params.get("date"))
    # Canonicals and aliases reserve the same PK, preventing a concurrent new
    # event from stealing a historical route. The pending reservation is linked
    # to the new event by its after_insert listener in the same transaction.
    for number in range(1, 10001):
        slug = base if number == 1 else f"{base}-{number}"
        try:
            with context.connection.begin_nested():
                context.connection.execute(
                    insert(EventSlugAlias).values(slug=slug, event_id=None)
                )
            return slug
        except IntegrityError:
            continue
    raise ValueError("Unable to reserve a unique event route")


def event_path(event):
    return f"/events/{event.slug}" if event.slug else f"/etkinlik/{event.id}"


def resolve_event_slug(db, slug, include_past=True):
    from ..models.event import Event, EventSlugAlias
    from ..services.event_lifecycle import history_event_filter, visible_event_filter
    from sqlalchemy import or_

    query = db.query(Event).outerjoin(
        EventSlugAlias, EventSlugAlias.event_id == Event.id
    )
    query = query.filter(or_(Event.slug == slug, EventSlugAlias.slug == slug))
    return (
        query.filter(history_event_filter()).first()
        if include_past
        else query.filter(*visible_event_filter()).first()
    )
