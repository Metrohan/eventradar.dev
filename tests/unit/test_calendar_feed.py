from datetime import datetime, timedelta, timezone
import re

from app.models.event import Event
from app.utils.event_dates import local_now


def test_calendar_visibility_and_dates(client, test_db):
    future = (local_now() + timedelta(days=10)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    for index, values in enumerate(
        [
            dict(date=future),
            dict(date=future.replace(hour=14, minute=30)),
            dict(date=None),
            dict(date=future, is_active=False),
            dict(date=future - timedelta(days=20)),
        ]
    ):
        test_db.add(
            Event(
                title=f"Event {index}",
                slug=f"event-{index}",
                url=f"https://source.example/{index}",
                source="test",
                **values,
            )
        )
    test_db.commit()
    response = client.get("/api/events/calendar.ics")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/calendar; charset=utf-8"
    text = response.text
    assert text.count("BEGIN:VEVENT") == 2
    assert "UID:event-0@eventradar.dev" in text
    assert f"DTSTART;VALUE=DATE:{future:%Y%m%d}" in text
    assert f"DTSTART:{future:%Y%m%d}T143000" in text
    assert "URL:https://eventradar.dev/events/event-0" in text
    assert "source.example" not in text
    assert re.search(r"DTSTAMP:\d{8}T\d{6}Z", text)
    assert "\n" not in text.replace("\r\n", "")


def test_calendar_escaping_folding_and_stable_uid():
    from app.services.calendar_service import build_events_calendar

    title = "İğş😀" * 40 + ",;\\\r\nInjected: value"
    event = Event(
        title=title,
        slug="stable",
        description="a,b;c\\d\rline\nnext",
        location="İstanbul; Salon, 1",
        date=datetime(2027, 1, 2, 9, 30),
    )
    text = build_events_calendar(
        [event], now=datetime(2026, 11, 14, tzinfo=timezone.utc)
    )
    assert all(len(line.encode("utf-8")) <= 75 for line in text.split("\r\n"))
    unfolded = text.replace("\r\n ", "")
    assert "\r\nInjected:" not in unfolded
    assert "DESCRIPTION:a\\,b\\;c\\\\d\\nline\\nnext" in unfolded
    assert "LOCATION:İstanbul\\; Salon\\, 1" in unfolded
    assert "DTSTAMP:20261114T000000Z" in unfolded
    assert "DTSTART:20270102T093000" in unfolded
    assert "UID:stable@eventradar.dev" in unfolded
    event.title = "Changed"
    assert "UID:stable@eventradar.dev" in build_events_calendar([event])


def test_calendar_empty():
    from app.services.calendar_service import build_events_calendar

    text = build_events_calendar([])
    assert text.startswith("BEGIN:VCALENDAR\r\nVERSION:2.0\r\n")
    assert text.endswith("END:VCALENDAR\r\n")
    assert "VEVENT" not in text


def test_aware_datetime_is_converted_to_istanbul_floating_time():
    from app.services.calendar_service import build_events_calendar

    event = Event(
        title="UTC event",
        slug="aware",
        date=datetime(2027, 1, 2, 9, 30, tzinfo=timezone.utc),
    )
    text = build_events_calendar([event])
    assert "DTSTART:20270102T123000\r\n" in text
    assert "DTSTART:20270102T093000Z" not in text
