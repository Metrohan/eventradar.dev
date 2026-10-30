from datetime import timedelta
from app.models.event import Event
from app.services.event_service import EventService
from app.schemas.event import EventCreate, EventUpdate
from app.utils.event_dates import local_now


def make_event(db, **overrides):
    data = dict(
        title="İstanbul Python Atölyesi",
        url="https://example.org/event",
        source="Example",
        date=local_now() + timedelta(days=10),
        description="<script>evil()</script>",
        location="İstanbul",
    )
    data.update(overrides)
    event = Event(**data)
    db.add(event)
    db.commit()
    return event


def test_slug_persists_after_title_update(test_db):
    event = make_event(test_db)
    slug = event.slug
    assert slug and "istanbul-python" in slug
    EventService(test_db).update_event(event.id, EventUpdate(title="Yeni başlık"))
    assert event.slug == slug


def test_duplicate_titles_have_distinct_slugs(test_db):
    first = make_event(test_db)
    second = make_event(test_db, url="https://example.org/second")
    assert first.slug != second.slug


def test_ssr_detail_and_legacy_redirect(client, test_db):
    event = make_event(test_db)
    response = client.get(f"/events/{event.slug}")
    assert response.status_code == 200
    assert "<h1>İstanbul Python Atölyesi</h1>" in response.text
    assert "&lt;script&gt;evil()&lt;/script&gt;" in response.text
    assert "<script>evil()" not in response.text
    assert f"https://eventradar.dev/events/{event.slug}" in response.text
    assert "application/ld+json" in response.text
    legacy = client.get(f"/etkinlik/{event.id}", follow_redirects=False)
    assert legacy.status_code == 301
    assert legacy.headers["location"] == f"/events/{event.slug}"


def test_hidden_missing_and_expired_pages(client, test_db):
    hidden = make_event(test_db, is_active=False, deactivation_reason="manual")
    assert client.get(f"/events/{hidden.slug}").status_code == 404
    assert client.get("/events/not-real").status_code == 404
    past = make_event(
        test_db, url="https://example.org/past", date=local_now() - timedelta(days=2)
    )
    response = client.get(f"/events/{past.slug}")
    assert response.status_code == 200
    assert "noindex, follow" in response.text
    assert "Etkinlik sona erdi" in response.text
    assert '"@type": "Event"' not in response.text


def test_application_deadline_is_not_an_event_date(test_db):
    event = EventService(test_db).create_event(
        EventCreate(
            title="Bootcamp",
            url="https://example.org/apply",
            source="Example",
            description="Son başvuru: 15 Aralık 2026",
        )
    )
    assert event.date is None


def test_closed_applications_do_not_hide_future_event(client, test_db):
    event = make_event(test_db, application_deadline=local_now() - timedelta(days=2))
    response = client.get(f"/events/{event.slug}")
    assert response.status_code == 200
    assert "Başvurular kapandı" in response.text
    assert "Etkinlik tarihi" in response.text
    assert "Son başvuru" in response.text


def test_category_and_city_pages_match_sitemap(client, test_db):
    from app.models.tag import Tag
    import xml.etree.ElementTree as ET

    tag = test_db.query(Tag).filter(Tag.name == "atolye").one()
    event = make_event(test_db)
    event.tags.append(tag)
    test_db.commit()
    for path in ["/kategoriler/atolye", "/sehirler/istanbul"]:
        response = client.get(path)
        assert response.status_code == 200
        assert event.title in response.text
        assert f"/events/{event.slug}" in response.text
    assert client.get("/sehirler/unknown").status_code == 404
    assert client.get("/kategoriler/unknown").status_code == 404
    sitemap = client.get("/sitemap.xml")
    root = ET.fromstring(sitemap.text)
    urls = {
        node.text
        for node in root.iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
    }
    assert f"https://eventradar.dev/events/{event.slug}" in urls
    assert "https://eventradar.dev/sehirler/istanbul" in urls
    assert "https://eventradar.dev/kategoriler/atolye" in urls
    assert not any("/etkinlik/" in url for url in urls)


def test_robots_allows_public_resources(client):
    from pathlib import Path
    from urllib.robotparser import RobotFileParser

    response = client.get("/robots.txt")
    assert response.status_code == 200
    fallback = (
        Path(__file__).resolve().parents[2] / "frontend/public/robots.txt"
    ).read_text()
    assert fallback == response.text
    # Python 3.11 uses the first matching rule, while newer parsers choose the
    # longest match. Public access is implicit: no broad Allow rule is needed.
    paths = {
        "/": True,
        "/events/example": True,
        "/sitemap.xml": True,
        "/api/events/rss": True,
        "/assets/example.js": True,
        "/admin/login": False,
        "/api/admin/events": False,
        "/docs": False,
        "/openapi.json": False,
    }
    for source, body in (("backend", response.text), ("fallback", fallback)):
        robots = RobotFileParser()
        robots.parse(body.splitlines())
        for agent in ("Googlebot", "bingbot", "OtherCrawler"):
            for path, allowed in paths.items():
                assert (
                    robots.can_fetch(agent, "https://eventradar.dev" + path) == allowed
                ), (
                    source,
                    agent,
                    path,
                )


def test_slug_migration_preserves_rows_and_roundtrips():
    import importlib.util
    from pathlib import Path
    from alembic.migration import MigrationContext
    from alembic.operations import Operations
    from sqlalchemy import create_engine, text, inspect

    spec = importlib.util.spec_from_file_location(
        "slug_revision",
        Path(__file__).resolve().parents[2]
        / "alembic/versions/a3b4c5d6e7f8_add_permanent_event_slugs.py",
    )
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    engine = create_engine("sqlite:///:memory:")
    with engine.begin() as connection:
        connection.execute(
            text("CREATE TABLE events (id INTEGER PRIMARY KEY, title VARCHAR(500))")
        )
        connection.execute(
            text("INSERT INTO events VALUES (1, 'Legacy'), (2, 'Legacy')")
        )
        with Operations.context(MigrationContext.configure(connection)):
            migration.upgrade()
            assert connection.execute(
                text("SELECT slug FROM events ORDER BY id")
            ).scalars().all() == ["etkinlik-1", "etkinlik-2"]
            assert not next(
                col
                for col in inspect(connection).get_columns("events")
                if col["name"] == "slug"
            )["nullable"]
            connection.execute(
                text("INSERT INTO events (id, title) VALUES (3, 'Old writer')")
            )
            old_slug = connection.execute(
                text("SELECT slug FROM events WHERE id=3")
            ).scalar()
            assert old_slug.startswith("etkinlik-") and old_slug != "etkinlik-1"
            migration.downgrade()
        assert connection.execute(text("SELECT count(*) FROM events")).scalar() == 3
    engine.dispose()


def test_explicit_deadline_time_expires_today(client, test_db, monkeypatch):
    from datetime import datetime

    now = datetime(2026, 10, 30, 18)
    monkeypatch.setattr("app.api.discovery.local_now", lambda: now)
    monkeypatch.setattr("app.api.discovery.day_start", lambda: now.replace(hour=0))
    event = make_event(test_db, application_deadline=now.replace(hour=10))
    assert "Başvurular kapandı" in client.get(f"/events/{event.slug}").text
    event.application_deadline = now.replace(hour=0)
    test_db.commit()
    assert "Başvurular kapandı" not in client.get(f"/events/{event.slug}").text
