from datetime import datetime, timezone

import pytest

from app.services.sitemap_service import build_sitemap, STATIC_PAGES, SITE_URL


def _make_event(id_: int, last_seen_at=None, is_active=True):
    from unittest.mock import MagicMock

    e = MagicMock()
    e.id = id_
    e.is_active = is_active
    e.last_seen_at = last_seen_at
    e.scraped_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
    return e


def _make_post(slug: str, created_at=None):
    from unittest.mock import MagicMock

    p = MagicMock()
    p.slug = slug
    p.is_published = True
    p.created_at = created_at
    return p


def test_sitemap_is_valid_xml():
    xml = build_sitemap([], [])
    assert xml.startswith('<?xml version="1.0"')
    assert "<urlset" in xml
    assert "</urlset>" in xml


def test_static_pages_present():
    xml = build_sitemap([], [])
    for path, _, _ in STATIC_PAGES:
        assert f"{SITE_URL}{path}" in xml


def test_event_url_included():
    event = _make_event(42)
    xml = build_sitemap([event], [])
    assert f"{SITE_URL}/etkinlik/42" in xml


def test_event_lastmod_from_last_seen_at():
    dt = datetime(2026, 6, 15, tzinfo=timezone.utc)
    event = _make_event(1, last_seen_at=dt)
    xml = build_sitemap([event], [])
    assert "2026-06-15" in xml


def test_blog_post_url_included():
    post = _make_post("haftalik-rehber-2026-08")
    xml = build_sitemap([], [post])
    assert f"{SITE_URL}/blog/haftalik-rehber-2026-08" in xml


def test_multiple_events_all_present():
    events = [_make_event(i) for i in range(1, 6)]
    xml = build_sitemap(events, [])
    for i in range(1, 6):
        assert f"/etkinlik/{i}" in xml


def test_special_chars_escaped():
    post = _make_post("a&b")
    xml = build_sitemap([], [post])
    assert "&amp;" in xml
    assert "&b" not in xml


def test_no_events_no_posts_returns_static_only():
    xml = build_sitemap([], [])
    assert xml.count("<url>") == len(STATIC_PAGES)
