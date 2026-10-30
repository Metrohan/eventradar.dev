"""Immutable stored slugs; title edits never change published URLs."""

import re
import unicodedata
from uuid import uuid4


def new_event_slug(context):
    title = context.get_current_parameters().get("title", "etkinlik")
    text = str(title).translate(str.maketrans("ıİşŞğĞüÜöÖçÇ", "iIsSgGuUoOcC"))
    text = (
        unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    )
    base = re.sub(r"[^a-z0-9]+", "-", text).strip("-")[:100] or "etkinlik"
    return f"{base}-{uuid4().hex}"


def event_path(event):
    return f"/events/{event.slug}" if event.slug else f"/etkinlik/{event.id}"
