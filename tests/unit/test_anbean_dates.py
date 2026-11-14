from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

from app.scrapers.anbean_scraper import scrape_anbean_events

LIST = """<div class="mini-eventCard"><a title="Talent Summit" href="/talent-summit-2027/"></a><div class="mini-eventCard-dates"><div class="mini-eventCard-dateItem"><span>Son Kayıt</span><span>19 Mart 2027</span></div></div></div>"""


def scrape(detail):
    responses = [Mock(content=LIST.encode()), Mock(content=detail.encode())]
    with patch("app.scrapers.anbean_scraper.requests.get", side_effect=responses):
        return scrape_anbean_events()[0]


def test_start_and_deadline_are_distinct():
    html = (Path(__file__).parents[1] / "fixtures/anbean_dates.html").read_text()
    event = scrape(html)
    assert event["date"] == datetime(2027, 3, 16, 11)
    assert event["application_deadline"] == datetime(2027, 3, 19, 16)


def test_deadline_only_never_becomes_start():
    event = scrape(
        '<title>Son Kayıt Tarihi: 19.03.2027</title><div class="eventDetail-rs-ie-rightWrapper"><span>Son Kayıt Tarihi</span><span>19 Mart 2027 16:00</span></div>'
    )
    assert event["date"] is None
    assert event["application_deadline"] == datetime(2027, 3, 19, 16)


def test_unrelated_description_dates_never_become_start():
    event = scrape("<p>2025 yılında kuruldu. Başvurular 19 Mart 2027 bitiyor.</p>")
    assert event["date"] is None


def test_start_without_year_stays_unknown():
    event = scrape(
        '<div class="eventDetail-rs-ie-rightWrapper"><span>Etkinlik Başlangıç / Bitiş Tarihleri</span><span>16 Mart 11:00</span><span>19 Mart 16:00</span></div>'
    )
    assert event["date"] is None
