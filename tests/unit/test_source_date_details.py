from datetime import datetime
from unittest.mock import Mock, patch
import sys


def parse_coderspace_events(*args, **kwargs):
    with patch.dict(sys.modules, {"undetected_chromedriver": Mock()}):
        from app.scrapers.cs_scraper import parse_coderspace_events as parse

        return parse(*args, **kwargs)


def test_coderspace_start_is_not_end_or_deadline():
    html = """<article><a href="/etkinlikler/test/"><img alt="Test" src="/test.jpg" /></a><h5><a>Test</a></h5><span>Başlangıç</span><span>19 Kasım 2026</span><span>Bitiş</span><span>22 Kasım 2026</span><span>Son Başvuru</span><span>18 Kasım 2026</span></article>"""
    e = parse_coderspace_events(html, now=datetime(2026, 11, 14))[0]
    assert e["date"] == "2026-11-19 00:00:00"
    assert e["application_deadline"] == "2026-11-18 00:00:00"


def test_coderspace_deadline_without_start_stays_undated():
    html = """<article><a href="/etkinlikler/test/"><img alt="Test" src="/test.jpg" /></a><span>Son Başvuru</span><span>18 Kasım 2026</span></article>"""
    assert parse_coderspace_events(html, now=datetime(2026, 11, 14))[0]["date"] is None


def test_youthall_detail_explicit_year_and_time():
    from app.scrapers.youthall_scraper import parse_youthall_detail_dates

    html = """<div class="c-job_detail_content_list_features"><h6>Etkinlik Başlangıç</h6><small>16 Aralık 2026 Çarşamba 11:00</small></div><div class="c-job_detail_content_list_features"><h6>Son Başvuru</h6><small>16 Aralık 2026 Çarşamba</small></div>"""
    assert parse_youthall_detail_dates(html) == (
        datetime(2026, 12, 16, 11),
        datetime(2026, 12, 16),
    )


def test_youthall_unlabeled_and_yearless_details_stay_unknown():
    from app.scrapers.youthall_scraper import parse_youthall_detail_dates

    html = '<p>16 Aralık 2026 11:00</p><div class="c-job_detail_content_list_features"><h6>Etkinlik Başlangıç</h6><small>16 Aralık 11:00</small></div>'
    assert parse_youthall_detail_dates(html) == (None, None)


def _card(start, deadline):
    return f'<article><a href="/etkinlikler/test/"><img alt="Test" src="/x" /></a><span>Başlangıç</span><span>{start}</span><span>Son Başvuru</span><span>{deadline}</span></article>'


def test_ongoing_coderspace_start_does_not_jump_to_next_year():
    e = parse_coderspace_events(
        _card("13 Kasım", "19 Kasım"), now=datetime(2026, 11, 14, 18)
    )[0]
    assert e["date"] == "2026-11-13 00:00:00"


def test_same_day_deadline_remains_open_without_explicit_time():
    e = parse_coderspace_events(
        _card("14 Kasım", "14 Kasım"), now=datetime(2026, 11, 14, 18)
    )[0]
    assert e["date"] == "2026-11-14 00:00:00"


def test_coderspace_new_year_uses_supplied_clock():
    e = parse_coderspace_events(_card("3 Ocak", "1 Ocak"), now=datetime(2026, 12, 30))[
        0
    ]
    assert e["date"] == "2027-01-03 00:00:00"
    assert e["application_deadline"] == "2027-01-01 00:00:00"


def test_youthall_enrichment_survives_one_detail_network_failure():
    import requests
    from unittest.mock import Mock, patch
    from app.scrapers.youthall_scraper import scrape_youthall_events

    cards = "".join(
        f'<article class="events-card"><a class="events-card__link" href="/tr/etkinlikler/{i}/"></a><h3 class="events-card__title">Event {i}</h3><div class="events-card__when"><span class="events-card__val">16 Aralık</span></div></article>'
        for i in range(2)
    )
    detail = '<div class="c-job_detail_content_list_features"><h6>Etkinlik Başlangıç</h6><small>16 Aralık 2026 Çarşamba 11:00</small></div>'
    responses = [Mock(text=cards), requests.Timeout(), Mock(text=detail)]
    with patch("app.scrapers.youthall_scraper.requests.get", side_effect=responses):
        events = scrape_youthall_events()
    assert len(events) == 2
    assert events[0]["date"].endswith("00:00:00")
    assert events[1]["date"] == "2026-12-16 11:00:00"
