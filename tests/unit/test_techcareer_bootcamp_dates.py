from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

from app.scrapers.techcareer_scraper import _fetch_event_details


def test_bootcamp_summary_date_is_not_application_deadline():
    html = (
        Path(__file__).parents[1] / "fixtures/techcareer_bootcamp_dates.html"
    ).read_text()
    response = Mock(text=html)
    with patch("app.scrapers.techcareer_scraper.requests.get", return_value=response):
        details = _fetch_event_details("https://www.techcareer.net/bootcamp/example")
    assert details["date"] == datetime(2026, 12, 7)


def test_deadline_alone_does_not_become_start_date():
    response = Mock(text="<h3>SON BAŞVURU</h3><p>25.11.2026</p>")
    with patch("app.scrapers.techcareer_scraper.requests.get", return_value=response):
        assert _fetch_event_details("https://example.org")["date"] is None


def test_invalid_bootcamp_date_stays_unknown():
    response = Mock(
        text='<p data-test="event-summary-education-date-content">31.02.2026 - 01.03.2026</p>'
    )
    with patch("app.scrapers.techcareer_scraper.requests.get", return_value=response):
        assert _fetch_event_details("https://example.org")["date"] is None


def test_existing_detail_template_takes_precedence():
    response = Mock(
        text='<p><strong>Tarih:</strong> 19 Temmuz 2027 | 11.00 - 12.00</p><p data-test="event-summary-education-date-content">07.12.2026 - 27.12.2026</p>'
    )
    with patch(
        "app.scrapers.techcareer_scraper.requests.get", return_value=response
    ), patch(
        "app.scrapers.techcareer_scraper.parse_relative_turkish_datetime",
        return_value=datetime(2027, 7, 19, 11),
    ):
        assert _fetch_event_details("https://example.org")["date"] == datetime(
            2027, 7, 19, 11
        )
