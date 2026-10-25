"""Regressions from the 2026-10-25 audit; all delivery is mocked."""

from dataclasses import replace
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import requests
from pydantic import ValidationError

from app.models.event import Event
from app.models.subscriber import Subscriber
from app.schemas.event import EventCreate, EventUpdate
from app.schemas.subscriber import BroadcastRequest
from app.services.event_ingestion import EventIngestion, ScrapedEvent
from app.services.event_service import EventService
from app.services.notification_service import NotificationService
from app.services.scrape_run import ScrapeRunCoordinator
from app.services.seo_head import _event_meta
from app.services.source_catalog import get_source

NOW = datetime(2027, 5, 15, 15)


def stored_event(db, **overrides):
    values = dict(
        title="Audit event",
        url="https://example.com/audit",
        source="Tech Istanbul",
        date=NOW + timedelta(days=10),
        is_active=True,
        last_seen_at=NOW - timedelta(days=5),
    )
    values.update(overrides)
    event = Event(**values)
    db.add(event)
    db.commit()
    return event


def test_empty_scrape_never_reconciles(test_db):
    from app.services.event_ingestion import IngestionResult

    source = replace(get_source("tech-istanbul"), runner=lambda: [])
    ingestion = MagicMock()
    ingestion.ingest.return_value = IngestionResult()
    ingestion.reconcile_source.return_value = 0
    coordinator = ScrapeRunCoordinator(lambda: test_db, lambda: ingestion)
    result = coordinator.run(source)
    assert result.status == "failed"
    ingestion.reconcile_source.assert_not_called()


def test_partial_ingestion_is_not_success_and_never_reconciles(test_db):
    from app.services.event_ingestion import IngestionResult

    source = replace(
        get_source("tech-istanbul"), runner=lambda: [{"title": "A", "url": "u"}]
    )
    ingestion = MagicMock()
    ingestion.ingest.return_value = IngestionResult(failed_urls=["u"])
    ingestion.reconcile_source.return_value = 0
    result = ScrapeRunCoordinator(lambda: test_db, lambda: ingestion).run(source)
    assert result.status == "failed"
    assert result.failed == 1
    ingestion.reconcile_source.assert_not_called()


@pytest.mark.parametrize(
    "module,function",
    [
        ("techistanbul_scraper", "scrape_techistanbul_events"),
        ("patika_scraper", "scrape_patika_events"),
        ("komunite_scraper", "scrape_komunite_events"),
        ("kodluyoruz_scraper", "scrape_kodluyoruz_events"),
        ("anbean_scraper", "scrape_anbean_events"),
    ],
)
def test_source_network_errors_reach_coordinator(module, function):
    from importlib import import_module

    scraper = import_module(f"app.scrapers.{module}")
    with patch.object(
        scraper.requests, "get", side_effect=requests.ConnectionError("offline")
    ):
        with pytest.raises(requests.RequestException):
            getattr(scraper, function)()


def test_missing_source_event_reactivates_when_seen_again(test_db):
    event = stored_event(test_db)
    url = event.url
    ingestion = EventIngestion(lambda: test_db, clock=lambda: NOW)
    assert ingestion.reconcile_source("Tech Istanbul") == 1
    ingestion.ingest(
        [
            ScrapedEvent(
                "Found again", url, "Tech Istanbul", date=NOW + timedelta(days=10)
            )
        ]
    )
    event = test_db.query(Event).filter(Event.url == url).one()
    assert event.is_active is True
    assert event.deactivation_reason is None


def test_manual_hidden_event_stays_hidden_on_scrape(test_db):
    service = EventService(test_db)
    event = service.create_event(
        EventCreate(title="Manual hide", url="https://example.com/manual", date=NOW)
    )
    event_id, url = event.id, event.url
    service.update_event(event_id, EventUpdate(is_active=False))
    EventIngestion(lambda: test_db, clock=lambda: NOW).ingest(
        [ScrapedEvent("Still hidden", url, "Admin", date=NOW + timedelta(days=5))]
    )
    event = test_db.query(Event).filter(Event.id == event_id).one()
    assert event.is_active is False
    assert event.deactivation_reason == "manual"


@pytest.mark.parametrize("reason", ["past", "missing"])
def test_admin_edit_preserves_automatic_reason_when_status_unchanged(test_db, reason):
    event = stored_event(test_db, is_active=False, deactivation_reason=reason)
    url = event.url
    updated = EventService(test_db).update_event(
        event.id, EventUpdate(title="New title", is_active=False)
    )
    assert updated.deactivation_reason == reason
    EventIngestion(lambda: test_db, clock=lambda: NOW).ingest(
        [ScrapedEvent("Found again", url, "Tech Istanbul", date=NOW)]
    )
    assert test_db.query(Event).filter(Event.url == url).one().is_active is True


@pytest.mark.parametrize(
    "bad",
    [
        {"title": "Malformed", "url": None},
        {"title": " ", "url": "https://example.com/blank"},
    ],
)
@pytest.mark.parametrize("mixed", [False, True])
def test_malformed_source_row_blocks_reconciliation(test_db, bad, mixed):
    event = stored_event(test_db)
    event_id = event.id
    ingestion = EventIngestion(lambda: test_db, clock=lambda: NOW)
    records = [bad] + (
        [{"title": "Valid", "url": "https://example.com/valid"}] if mixed else []
    )
    source = replace(get_source("tech-istanbul"), runner=lambda: records)
    result = ScrapeRunCoordinator(lambda: test_db, lambda: ingestion).run(source)
    assert result.status == "failed"
    assert result.failed == 1
    assert result.deactivated == 0
    assert test_db.query(Event).filter(Event.id == event_id).one().is_active is True


def test_legacy_unknown_inactive_event_stays_hidden(test_db):
    event = stored_event(test_db, is_active=False)
    url = event.url
    EventIngestion(lambda: test_db, clock=lambda: NOW).ingest(
        [ScrapedEvent("Unknown reason", url, "Tech Istanbul", date=NOW)]
    )
    assert test_db.query(Event).filter(Event.url == url).one().is_active is False


def test_today_date_only_event_is_not_deactivated(test_db):
    stored_event(test_db, date=NOW.replace(hour=0))
    assert EventIngestion(lambda: test_db, clock=lambda: NOW).deactivate_past() == 0


def test_today_visibility_uses_istanbul_day_even_when_host_is_utc(test_db):
    event = stored_event(test_db, date=NOW.replace(hour=0))
    with patch("app.utils.event_dates.local_now", return_value=NOW):
        service = EventService(test_db)
        assert service.get_total_active_events() == 1
        assert service.get_public_event_by_id(event.id) is not None


def test_history_lists_expired_events_without_exposing_hides(client, test_db):
    past = stored_event(
        test_db,
        is_active=False,
        deactivation_reason="past",
        date=NOW - timedelta(days=400),
    )
    past_id = past.id
    stored_event(
        test_db,
        url="https://example.com/hidden",
        is_active=False,
        deactivation_reason="manual",
    )
    stored_event(test_db, url="https://example.com/unknown", is_active=False)
    response = client.get("/api/events?active_only=false")
    assert response.status_code == 200
    assert [event["id"] for event in response.json()["events"]] == [past_id]
    assert client.get(f"/api/events/{past_id}").status_code == 404
    assert client.get(f"/api/events/{past_id}?include_past=true").status_code == 200
    assert client.get("/api/events/2?include_past=true").status_code == 404


def test_both_sitemaps_use_same_visibility_and_renderer(client, test_db):
    past = stored_event(test_db, date=datetime.now() - timedelta(days=400))
    past_id = past.id
    root = client.get("/sitemap.xml")
    alternate = client.get("/api/events/sitemap.xml")
    assert root.status_code == alternate.status_code == 200
    assert root.text == alternate.text
    assert f"/etkinlik/{past_id}</loc>" not in root.text


def test_broadcast_excludes_unconfirmed_email_but_keeps_telegram(test_db):
    test_db.add_all(
        [
            Subscriber(
                contact_info="pending@example.com", channel="email", confirmed=False
            ),
            Subscriber(
                contact_info="ready@example.com", channel="email", confirmed=True
            ),
            Subscriber(contact_info="1234", channel="telegram", confirmed=False),
        ]
    )
    test_db.commit()
    service = NotificationService(test_db)
    with patch.object(service, "_send_email") as mail, patch.object(
        service, "_send_telegram"
    ) as telegram:
        result = service.broadcast_message(BroadcastRequest(message="Audit broadcast"))
    assert [call.args[0] for call in mail.call_args_list] == ["ready@example.com"]
    telegram.assert_called_once()
    assert result["recipient_count"] == 2


def test_broadcast_uses_shared_smtp_and_propagates_failed_delivery(test_db):
    service = NotificationService(test_db)
    with patch("app.services.email_service._send", return_value=False) as send:
        with pytest.raises(RuntimeError):
            service._send_email("test@example.com", "Subject", "<not html>", "token")
    send.assert_called_once()
    assert "&lt;not html&gt;" in send.call_args.args[2]


@pytest.mark.parametrize("schema", [EventCreate, EventUpdate])
@pytest.mark.parametrize(
    "field,value",
    [
        ("title", " "),
        ("source", " "),
        ("url", "javascript:alert(1)"),
        ("url", "//example.com"),
        ("title", "x" * 501),
    ],
)
def test_event_schema_rejects_invalid_facts(schema, field, value):
    values = {"title": "Valid", "url": "https://example.com/event", field: value}
    with pytest.raises(ValidationError):
        schema(**values)


def test_event_schema_normalizes_blank_dates_and_aware_times():
    data = EventCreate(
        title="Event", url="https://example.com/event", date="", application_deadline=""
    )
    assert data.date is None and data.application_deadline is None
    update = EventUpdate(date="2027-05-15T12:00:00Z")
    assert update.date == NOW


def test_seo_does_not_invent_price_availability_or_missing_location(test_db):
    event = stored_event(test_db, location=None)
    meta = _event_meta(event)
    schema = meta.json_ld[0][1]
    assert "isAccessibleForFree" not in schema
    assert "offers" not in schema
    assert "location" not in schema
    assert "eventAttendanceMode" not in schema
    assert "Ücretsiz" not in meta.description


def test_ci_uses_image_constraints():
    root = Path(__file__).resolve().parents[2]
    for name in ("test.yml", "deploy.yml"):
        workflow = (root / ".github/workflows" / name).read_text()
        install = next(
            line
            for line in workflow.splitlines()
            if "pip install -r requirements.txt" in line
        )
        assert "-c constraints.txt" in install
