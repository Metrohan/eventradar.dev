"""Naive event timestamps represent Europe/Istanbul wall-clock time."""

from datetime import datetime
from zoneinfo import ZoneInfo

ISTANBUL = ZoneInfo("Europe/Istanbul")


def local_now() -> datetime:
    return datetime.now(ISTANBUL).replace(tzinfo=None)


def local_datetime(value: datetime) -> datetime:
    if value.tzinfo is not None:
        return value.astimezone(ISTANBUL).replace(tzinfo=None)
    return value


def day_start(now: datetime | None = None) -> datetime:
    return local_datetime(now or local_now()).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
