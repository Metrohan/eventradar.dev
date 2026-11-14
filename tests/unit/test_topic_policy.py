from datetime import datetime
from sqlalchemy.orm import sessionmaker
from app.models.event import Event
from app.services.topic_policy import is_technical_event
from app.services.event_ingestion import EventIngestion, ScrapedEvent


def test_technical_content_required_not_format():
    for title in [
        "Python Atölyesi",
        "Siber Güvenlik Okulu",
        "Data Engineering Bootcamp",
        "AI Writing Bootcamp",
        "No-Code MVP",
        "Elektronik ve Gömülü Sistemler",
        "Computer Science Days",
    ]:
        assert is_technical_event(title)
    for title in [
        "Engineering Career Summit",
        "Talent Summit",
        "Girişimcilik Okulu Çocuk",
        "Payroll Forecast 2027",
        "Cool Chain Club",
        "Bootcamp",
        "Hackathon",
        "Seminer",
        "Penti Retail Challenge",
    ]:
        assert not is_technical_event(title)
    assert not is_technical_event(
        "Talent Summit", "Python yazılım kariyeri hakkında genel bir buluşma"
    )
    assert is_technical_event(
        "One-Person Company Bootcamp", "AI agent ile otomasyon geliştirme"
    )


def test_scope_hide_restore_and_manual_hide(test_db):
    factory = sessionmaker(bind=test_db.get_bind())
    sent = []
    service = EventIngestion(
        factory,
        sent.append,
        topic_filter=is_technical_event,
        clock=lambda: datetime(2026, 11, 14),
    )
    url = "https://example.org/topic"
    service.ingest([ScrapedEvent(title="Talent Summit", url=url, source="Anbean")])
    row = test_db.query(Event).filter(Event.url == url).one()
    assert not row.is_active and row.deactivation_reason == "topic"
    assert not sent
    service.ingest([ScrapedEvent(title="Python Atölyesi", url=url, source="Anbean")])
    test_db.expire_all()
    assert row.is_active and row.deactivation_reason is None
    row.is_active, row.deactivation_reason = False, "manual"
    test_db.commit()
    service.ingest([ScrapedEvent(title="Python Atölyesi", url=url, source="Anbean")])
    test_db.expire_all()
    assert not row.is_active and row.deactivation_reason == "manual"


def test_topic_hidden_records_not_public(client, test_db):
    e = Event(
        title="Talent Summit",
        slug="topic-test",
        url="https://example.org/test",
        source="Anbean",
        is_active=False,
        deactivation_reason="topic",
    )
    test_db.add(e)
    test_db.commit()
    assert client.get("/events/topic-test").status_code == 404
    assert client.get(f"/api/events/{e.id}?include_past=true").status_code == 404
    assert not client.get("/api/events?active_only=false").json()["events"]
    assert "topic-test" not in client.get("/api/events/calendar.ics").text


def test_production_factory_enables_scope_policy():
    from app.services.event_ingestion import build_event_ingestion

    assert build_event_ingestion()._topic_filter is is_technical_event


def test_international_network_is_not_a_technical_topic():
    assert not is_technical_event(
        "MAKE IT BRIGHT 2026",
        "Grow your international network and win a graduate traineeship",
    )
    assert is_technical_event(
        "One-Person Company Bootcamp",
        "Onay kapılı sekiz Claude agent ile otomasyon kur",
    )
    assert is_technical_event(
        "Go-to-Market Engineering Bootcamp", "Tekrarlanan bir Claude fabrikası kur"
    )


def test_topic_plan_apply_rollback_and_stale_guard(test_db):
    import pytest
    from scripts.review_topic_scope import plan_changes, apply_plan

    e = Event(
        title="Talent Summit",
        url="https://example.org/plan",
        source="Anbean",
        is_active=True,
    )
    test_db.add(e)
    test_db.commit()
    changes = plan_changes([e])
    assert len(changes) == 1
    assert e.is_active
    apply_plan(test_db, changes)
    assert not e.is_active and e.deactivation_reason == "topic"
    apply_plan(test_db, changes, rollback=True)
    assert e.is_active and e.deactivation_reason is None
    e.title = "Manual edit"
    test_db.commit()
    with pytest.raises(ValueError, match="snapshot changed"):
        apply_plan(test_db, changes)
    assert e.is_active


def test_cpp_and_csharp_are_technical():
    assert is_technical_event("C++ Atölyesi")
    assert is_technical_event("C# ve .NET Eğitimi")


def test_scope_sweep_hides_non_technical_history(client, test_db):
    from scripts.review_topic_scope import plan_changes, apply_plan

    e = Event(
        title="Talent Summit",
        slug="past-topic",
        url="https://example.org/past-topic",
        source="Anbean",
        is_active=False,
        deactivation_reason="past",
    )
    test_db.add(e)
    test_db.commit()
    changes = plan_changes([e])
    assert len(changes) == 1
    apply_plan(test_db, changes)
    assert e.deactivation_reason == "topic"
    assert client.get("/events/past-topic").status_code == 404
    assert not client.get("/api/events?active_only=false").json()["events"]


def test_partial_update_keeps_existing_technical_evidence(test_db):
    service = EventIngestion(
        sessionmaker(bind=test_db.get_bind()), topic_filter=is_technical_event
    )
    url = "https://example.org/evidence"
    service.ingest(
        [
            ScrapedEvent(
                title="One-Person Company Bootcamp",
                description="Claude agent atölyesi",
                url=url,
                source="Komünite",
            )
        ]
    )
    service.ingest(
        [
            ScrapedEvent(
                title="One-Person Company Bootcamp",
                description=None,
                url=url,
                source="Komünite",
            )
        ]
    )
    test_db.expire_all()
    assert test_db.query(Event).filter(Event.url == url).one().is_active
