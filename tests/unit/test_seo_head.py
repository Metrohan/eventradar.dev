import html
import json
import re
from datetime import datetime, timedelta

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api import public
from app.core.database import get_db
from app.models.blog_post import BlogPost
from app.models.event import Event
from app.services.seo_head import DEFAULT_TITLE, build_head

FUTURE = datetime.now() + timedelta(days=10)


def _event(db, **over):
    fields = dict(
        title="Hackathon 2026",
        url="https://youthall.com/events/h",
        source="Youthall",
        date=FUTURE.replace(microsecond=0),
        location="İstanbul",
        description="Güzel bir etkinlik",
        thumbnail_url="/media/thumbnails/card.webp",
    )
    fields.update(over)
    event = Event(**fields)
    db.add(event)
    db.commit()
    return event


def _ld(head, script_id):
    match = re.search(rf'<script id="{script_id}"[^>]*>(.*?)</script>', head, re.S)
    return json.loads(match.group(1)) if match else None


def test_home_is_indexable_with_default_tags_and_bare_canonical(test_db):
    head = build_head("/", test_db)

    assert f"<title>{html.escape(DEFAULT_TITLE)}</title>" in head
    assert 'content="index, follow"' in head
    assert '<link rel="canonical" href="https://eventradar.dev" />' in head


def test_landing_page_has_its_own_title_and_canonical(test_db):
    head = build_head("/hackathonlar/", test_db)  # trailing slash tolerated

    assert "<title>Hackathon Etkinlikleri | TechEventRadar</title>" in head
    assert 'href="https://eventradar.dev/hackathonlar"' in head


@pytest.mark.parametrize(
    "path", ["/yok-boyle-123", "/admin/login", "/etkinlik/abc", ""]
)
def test_unknown_paths_are_noindex_without_canonical(test_db, path):
    head = build_head(path, test_db) if path else build_head("/yok", test_db)

    assert 'content="noindex, follow"' in head
    assert "canonical" not in head
    assert "og:url" not in head


def test_event_head_carries_card_image_canonical_and_json_ld(test_db):
    event = _event(test_db)

    head = build_head(f"/etkinlik/{event.id}", test_db)

    assert "<title>Hackathon 2026 | TechEventRadar</title>" in head
    assert f'href="https://eventradar.dev/events/{event.slug}"' in head
    assert (
        'og:image" content="https://eventradar.dev/media/thumbnails/card.webp"' in head
    )
    schema = _ld(head, "event-jsonld")
    assert schema["startDate"] == FUTURE.replace(microsecond=0).isoformat()
    assert "+" not in schema["startDate"] and "Z" not in schema["startDate"]
    assert schema["eventAttendanceMode"].endswith("OfflineEventAttendanceMode")
    assert schema["location"]["@type"] == "Place"
    assert _ld(head, "breadcrumb-jsonld")["@type"] == "BreadcrumbList"


def test_online_event_is_marked_online(test_db):
    event = _event(test_db, location="Online")

    schema = _ld(build_head(f"/etkinlik/{event.id}", test_db), "event-jsonld")

    assert schema["eventAttendanceMode"].endswith("OnlineEventAttendanceMode")
    assert schema["location"] == {
        "@type": "VirtualLocation",
        "url": "https://youthall.com/events/h",
    }


def test_event_without_date_gets_no_event_json_ld(test_db):
    event = _event(test_db, date=None)

    head = build_head(f"/etkinlik/{event.id}", test_db)

    assert _ld(head, "event-jsonld") is None
    assert _ld(head, "breadcrumb-jsonld") is not None
    assert 'content="index, follow"' in head


def test_event_without_card_falls_back_to_banner(test_db):
    event = _event(test_db, thumbnail_url=None)

    head = build_head(f"/etkinlik/{event.id}", test_db)

    assert 'og:image" content="https://eventradar.dev/banner.png"' in head
    assert "image" not in _ld(head, "event-jsonld")


@pytest.mark.parametrize(
    "over", [dict(is_active=False), dict(date=datetime.now() - timedelta(days=1))]
)
def test_inactive_or_past_event_is_noindex(test_db, over):
    event = _event(test_db, **over)

    head = build_head(f"/etkinlik/{event.id}", test_db)

    assert 'content="noindex, follow"' in head
    assert event.title not in head


def test_missing_event_is_noindex(test_db):
    assert 'content="noindex, follow"' in build_head("/etkinlik/999999", test_db)


def test_hostile_text_cannot_break_out_of_tags_or_inject_ssi(test_db):
    evil = '</title><script>alert(1)</script><!--# include virtual="/x" --> "q"'
    event = _event(test_db, title=evil, description=evil, location=evil)

    head = build_head(f"/etkinlik/{event.id}", test_db)

    assert "<script>alert" not in head
    assert "</title><script" not in head
    assert "<!--#" not in head
    schema = _ld(head, "event-jsonld")  # still valid JSON after escaping
    assert schema["name"] == evil


def test_blog_post_head_only_for_published_posts(test_db):
    for slug, published in (("hafta-1", True), ("taslak", False)):
        test_db.add(
            BlogPost(
                slug=slug,
                title=f"Yazı {slug}",
                summary="Özet metni",
                content="x",
                week_start=datetime(2026, 1, 5 if published else 12).date(),
                week_end=datetime(2026, 1, 11 if published else 18).date(),
                is_published=published,
            )
        )
    test_db.commit()

    live = build_head("/blog/hafta-1", test_db)
    draft = build_head("/blog/taslak", test_db)

    assert "<title>Yazı hafta-1 | TechEventRadar</title>" in live
    assert 'href="https://eventradar.dev/blog/hafta-1"' in live
    assert 'content="noindex, follow"' in draft


def test_endpoint_returns_html_fragment(test_db):
    app = FastAPI()
    app.include_router(public.router, prefix="/api")
    app.dependency_overrides[get_db] = lambda: test_db
    with TestClient(app) as client:
        response = client.get("/api/seo/head/hackathonlar")
        root = client.get("/api/seo/head/")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "Hackathon Etkinlikleri" in response.text
    assert f"<title>{html.escape(DEFAULT_TITLE)}</title>" in root.text
