from datetime import datetime, timedelta

from app.models.event import Event
from app.services.event_ingestion import (
    EventIngestion,
    ScrapedEvent,
    normalize_date,
)


def test_normalize_date_values():
    value = datetime(2027, 5, 15)

    assert normalize_date(None) is None
    assert normalize_date("") is None
    assert normalize_date("tarih belirtilmemiş") is None
    assert normalize_date("-") is None
    assert normalize_date(value) == value
    assert normalize_date("15 Mayıs 2027").month == 5


def test_ingest_returns_typed_counts_and_deduplicates_batch(test_db):
    now = datetime(2026, 7, 11, 12, 0)
    ingestion = EventIngestion(lambda: test_db, clock=lambda: now)
    event = ScrapedEvent(
        title="Test",
        url="https://example.com/dup",
        source="test",
        date="01 Ocak 2027",
    )

    result = ingestion.ingest([event, event])

    assert result.new == 1
    assert result.updated == 0
    assert result.failed == 0
    assert result.summary() == "New: 1, Updated: 0"
    stored = test_db.query(Event).filter(Event.url == event.url).one()
    assert stored.last_seen_at == now


def test_ingest_creates_past_event_as_inactive(test_db):
    ingestion = EventIngestion(lambda: test_db)
    event = ScrapedEvent(
        title="Already Finished",
        url="https://example.com/already-finished",
        source="test",
        date=datetime.now() - timedelta(days=30),
    )

    result = ingestion.ingest([event])

    stored = test_db.query(Event).filter(Event.url == event.url).one()
    assert result.new == 1
    assert stored.is_active is False


def test_ingest_notifies_new_events_after_commit(test_db):
    notifications = []
    ingestion = EventIngestion(lambda: test_db, notifications.append)
    event = ScrapedEvent(
        title="New Event",
        url="https://example.com/new",
        source="test",
    )

    result = ingestion.ingest([event])

    assert result.notification_error is None
    assert notifications[0][0]["url"] == event.url
    assert test_db.query(Event).filter(Event.url == event.url).count() == 1


def test_notification_failure_is_non_fatal(test_db):
    def fail_notification(_events):
        raise RuntimeError("telegram unavailable")

    ingestion = EventIngestion(lambda: test_db, fail_notification)
    event = ScrapedEvent(
        title="New Event",
        url="https://example.com/notification-failure",
        source="test",
    )

    result = ingestion.ingest([event])

    assert result.new == 1
    assert result.notification_error == "telegram unavailable"


def test_invalid_record_does_not_abort_valid_records(test_db):
    ingestion = EventIngestion(lambda: test_db)
    invalid = ScrapedEvent(
        title=None,
        url="https://example.com/invalid",
        source="test",
    )
    valid = ScrapedEvent(
        title="Valid",
        url="https://example.com/valid",
        source="test",
    )

    result = ingestion.ingest([invalid, valid])

    assert result.new == 1
    assert result.failed_urls == ["https://example.com/invalid"]
    assert test_db.query(Event).filter(Event.url == valid.url).count() == 1


def test_deactivate_past_events(test_db):
    past = Event(
        title="Past Event",
        url="https://example.com/past",
        source="test",
        is_active=True,
        date=datetime.now() - timedelta(days=2),
        scraped_at=datetime.now(),
    )
    future = Event(
        title="Future Event",
        url="https://example.com/future",
        source="test",
        is_active=True,
        date=datetime.now() + timedelta(days=2),
        scraped_at=datetime.now(),
    )
    test_db.add_all([past, future])
    test_db.commit()
    past_id = past.id
    future_id = future.id
    ingestion = EventIngestion(lambda: test_db)

    count = ingestion.deactivate_past()

    assert count == 1
    stored_past = test_db.query(Event).filter(Event.id == past_id).one()
    stored_future = test_db.query(Event).filter(Event.id == future_id).one()
    assert stored_past.is_active is False
    assert stored_future.is_active is True


def test_reconcile_source_deactivates_only_stale_missing_events(test_db):
    now = datetime(2026, 7, 11, 12, 0)
    stale = Event(
        title="Missing",
        url="https://example.com/missing",
        source="Tech Istanbul",
        is_active=True,
        scraped_at=now - timedelta(days=10),
        last_seen_at=now - timedelta(days=4),
    )
    recent = Event(
        title="Recent",
        url="https://example.com/recent",
        source="Tech Istanbul",
        is_active=True,
        scraped_at=now,
        last_seen_at=now - timedelta(days=2),
    )
    other_source = Event(
        title="Other",
        url="https://example.com/other",
        source="Youthall",
        is_active=True,
        scraped_at=now - timedelta(days=10),
        last_seen_at=now - timedelta(days=10),
    )
    test_db.add_all([stale, recent, other_source])
    test_db.commit()
    ids = stale.id, recent.id, other_source.id
    ingestion = EventIngestion(lambda: test_db, clock=lambda: now)

    count = ingestion.reconcile_source("Tech Istanbul")

    states = [
        test_db.query(Event).filter(Event.id == event_id).one().is_active
        for event_id in ids
    ]
    assert count == 1
    assert states == [False, True, True]
