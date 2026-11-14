"""RFC 5545 feed. Naive event times are floating Istanbul wall-clock times."""

from datetime import datetime, timezone
from typing import cast

from ..models.event import Event
from ..utils.event_dates import local_datetime
from ..utils.event_urls import event_path

SITE_URL = "https://eventradar.dev"


def _text(value: object) -> str:
    return (
        str(value or "")
        .replace("\\", "\\\\")
        .replace("\r\n", "\n")
        .replace("\r", "\n")
        .replace("\n", "\\n")
        .replace(";", "\\;")
        .replace(",", "\\,")
    )


def _fold(line: str) -> str:
    # Fold by UTF-8 octets, never splitting a code point. The continuation
    # space counts toward the next physical line's 75-octet limit.
    parts = []
    current = ""
    size = 0
    for char in line:
        width = len(char.encode("utf-8"))
        if size + width > 75:
            parts.append(current)
            current, size = " ", 1
        current += char
        size += width
    parts.append(current)
    return "\r\n".join(parts)


def build_events_calendar(events: list[Event], now: datetime | None = None) -> str:
    stamp = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//EventRadar//Events//TR",
        "CALSCALE:GREGORIAN",
    ]
    for event in sorted(events, key=lambda item: str(item.slug)):
        if event.date is None:
            continue
        date = local_datetime(cast(datetime, event.date))
        # Midnight is this model's existing date-only sentinel.
        start = (
            "DTSTART;VALUE=DATE:" + date.strftime("%Y%m%d")
            if date.time().isoformat() == "00:00:00"
            else "DTSTART:" + date.strftime("%Y%m%dT%H%M%S")
        )
        lines.extend(
            [
                "BEGIN:VEVENT",
                f"UID:{event.slug}@eventradar.dev",
                "DTSTAMP:" + stamp.strftime("%Y%m%dT%H%M%SZ"),
                start,
                "SUMMARY:" + _text(event.title),
                f"URL:{SITE_URL}{event_path(event)}",
                "LOCATION:" + _text(event.location),
                "DESCRIPTION:" + _text(event.description),
                "END:VEVENT",
            ]
        )
    lines.append("END:VCALENDAR")
    return "\r\n".join(_fold(line) for line in lines) + "\r\n"
