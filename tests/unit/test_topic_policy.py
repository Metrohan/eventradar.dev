import pytest
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from app.models.event import Event
from app.utils.topic_policy import classify_event, is_technical_event
from app.services.event_ingestion import EventIngestion, ScrapedEvent


@pytest.mark.parametrize(
    ("title", "source", "tier"),
    [
        # 1. a technical term in the title
        ("Python Atölyesi", "Anbean", "technical"),
        ("Siber Güvenlik Okulu", "Anbean", "technical"),
        ("Data Engineering Bootcamp", "Tech Istanbul", "technical"),
        ("AI & Data Career Summit", "Youthall", "technical"),
        ("Elektronik ve Gömülü Sistemler", None, "technical"),
        # 2. a tech-career / role term in the title: relevant, not technical content
        ("Engineering Career Summit (Online)", "Youthall", "adjacent"),
        (
            "Sektör Buluşmaları Bir CTO’nun Deneyimleri ve Güncel Ajandası",
            "Anbean",
            "adjacent",
        ),
        ("Stellar Pro Hackathon - 720.000 TL Ödül Havuzu", "Patika.dev", "adjacent"),
        ("Grid Up Datathon", "Youthall", "adjacent"),
        ("Startup Pitch Günü", "Komünite", "adjacent"),
        ("Product Management 101", "Komünite", "adjacent"),
        ("Hackathon", None, "adjacent"),
        # every career summit stays: the site does not judge which are "tech enough"
        ("Aegean Career Summit #2", "Youthall", "adjacent"),
        ("Insurance & More Career Summit", "Youthall", "adjacent"),
        ("Diversity & Inclusion Career Summit", "Youthall", "adjacent"),
        ("Kariyer Zirvesi 2026", "Anbean", "adjacent"),
        # 4. a source that only lists technology events
        ("Temel Excel", "Pupilica", "source"),
        ("Robot Kol Atölyesi Özel Programı", "Coderspace", "source"),
        ("Kariyer Pusulası", "Kodluyoruz", "source"),
        ("Geleceği Yazanlar BiP Night", "coderspace", "source"),  # case-insensitive
    ],
)
def test_relevant_to_a_tech_audience_is_kept(title, source, tier):
    decision = classify_event(title, None, source)
    assert decision.allowed and decision.tier == tier
    assert is_technical_event(title, None, source)


@pytest.mark.parametrize(
    ("title", "source"),
    [
        # a format word alone is not evidence
        ("Bootcamp", None),
        ("Seminer", None),
        ("YouTalkZ", "Youthall"),
        ("BUEC Enerji Zirvesi", "Youthall"),
        ("Neova Ideathon", "Youthall"),
        # explicit non-tech topics
        ("Talent Summit", "Anbean"),
        ("Girişimcilik Okulu Çocuk", "Pupilica"),  # beats the tech source
        ("Payroll Forecast 2027", "Komünite"),
        ("Cool Chain Club", "Anbean"),
        ("Nestlé Youth Academy", "Anbean"),
        ("Penti Retail Challenge", "Anbean"),
        ("FMCG Camp", "Anbean"),
        ("Girişimciler için Markalaşma ve Pazarlama Stratejileri", "Tech Istanbul"),
        ("Girişimciler için Yatırıma Hazırlık Semineri", "Tech Istanbul"),
        ("CEF ile Finans Eğitimi", "Akbank Gençlik Akademisi"),
    ],
)
def test_without_tech_relevance_is_hidden(title, source):
    decision = classify_event(title, None, source)
    assert not decision.allowed and decision.tier == "general"


@pytest.mark.parametrize(
    "title",
    [
        "Bir CTO’nun Deneyimleri",
        "CTO'nun Günlüğü",
        "Python'da Asenkron",
        "AI’ın Geleceği",
    ],
)
def test_a_turkish_suffix_after_an_apostrophe_keeps_the_term(title):
    assert is_technical_event(title, None, "Anbean")


def test_description_only_evidence_counts_but_not_against_a_non_tech_title():
    assert is_technical_event(
        "Sıfırdan Bire", "Yapay zeka ile ürün geliştirme", "Komünite"
    )
    assert not is_technical_event(
        "Talent Summit", "Python yazılım kariyeri hakkında genel bir buluşma"
    )
    assert not is_technical_event(
        "Payroll Forecast 2027",
        "Bordroyu yapay zekâ destekli senaryolarla kur",
        "Komünite",
    )
    # "engineer" in the description is not a title-level role term
    assert not is_technical_event(
        "Food Science Day", "Gıda mühendisleriyle bir gün", "Anbean"
    )
    assert is_technical_event(
        "One-Person Company Bootcamp", "AI agent ile otomasyon geliştirme"
    )


def test_decision_carries_a_reason_for_review():
    assert classify_event("Engineering Career Summit").reason == "title: engineering"
    assert classify_event("Talent Summit").reason == "not tech: talent summit"
    assert (
        classify_event("Temel Excel", None, "Pupilica").reason
        == "tech source: Pupilica"
    )
    assert classify_event("Bootcamp").reason == "no technical evidence"


def test_ingestion_passes_the_source_to_the_policy(test_db):
    service = EventIngestion(
        sessionmaker(bind=test_db.get_bind()),
        topic_filter=is_technical_event,
        clock=lambda: datetime(2026, 11, 14),
    )
    service.ingest(
        [
            ScrapedEvent(
                title="Temel Excel", url="https://example.org/a", source="Pupilica"
            ),
            ScrapedEvent(
                title="Temel Excel", url="https://example.org/b", source="Anbean"
            ),
        ]
    )
    rows = {r.url: r for r in test_db.query(Event).all()}
    assert rows["https://example.org/a"].is_active
    assert not rows["https://example.org/b"].is_active
    assert rows["https://example.org/b"].deactivation_reason == "topic"


def test_plan_rows_say_why_an_event_is_hidden(test_db):
    from scripts.review_topic_scope import plan_changes

    e = Event(
        title="Talent Summit",
        url="https://example.org/why",
        source="Anbean",
        is_active=True,
    )
    test_db.add(e)
    test_db.commit()
    assert plan_changes([e])[0]["reason"] == "general: not tech: talent summit"


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


def test_production_does_not_hide_events_by_topic():
    from app.services.event_ingestion import build_event_ingestion

    assert build_event_ingestion()._topic_filter is None


def test_a_scrape_reopens_a_topic_hidden_event_when_no_filter_is_set(test_db):
    url = "https://example.org/reopen"
    row = Event(
        title="Talent Summit",
        url=url,
        source="Anbean",
        date=datetime(2026, 12, 10),
        is_active=False,
        deactivation_reason="topic",
    )
    test_db.add(row)
    test_db.commit()
    service = EventIngestion(
        sessionmaker(bind=test_db.get_bind()), clock=lambda: datetime(2026, 11, 15)
    )

    service.ingest(
        [
            ScrapedEvent(
                title="Talent Summit", url=url, source="Anbean", date="2026-12-10"
            )
        ]
    )

    test_db.expire_all()
    assert row.is_active and row.deactivation_reason is None


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
