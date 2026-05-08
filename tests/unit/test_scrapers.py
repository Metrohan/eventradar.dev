import os

os.environ.setdefault("ALLOW_INSECURE_DEFAULTS", "true")
os.environ.setdefault("SECRET_KEY", "test-secret-key-that-is-at-least-32-chars")
os.environ.setdefault("ADMIN_USERNAME", "testadmin")
os.environ.setdefault("ADMIN_PASSWORD", "testpassword")

from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

FIXTURES = Path(__file__).parent.parent / "fixtures"


def _html(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def _make_selenium_driver(html: str) -> MagicMock:
    driver = MagicMock()
    driver.page_source = html
    return driver


# ── Youthall ──────────────────────────────────────────────────────────────────


def test_youthall_returns_events():
    from app.scrapers.youthall_scraper import scrape_youthall_events

    mock_driver = _make_selenium_driver(_html("youthall.html"))

    with patch(
        "app.scrapers.youthall_scraper.ensure_chromedriver",
        return_value="/usr/bin/chromedriver",
    ), patch(
        "app.scrapers.youthall_scraper.webdriver.Chrome", return_value=mock_driver
    ), patch(
        "app.scrapers.youthall_scraper.time.sleep"
    ):
        events = scrape_youthall_events()

    assert isinstance(events, list)
    assert len(events) >= 1
    assert all("title" in e for e in events)
    assert all("url" in e for e in events)


def test_youthall_no_chromedriver_returns_empty():
    from app.scrapers.youthall_scraper import scrape_youthall_events

    with patch("app.scrapers.youthall_scraper.ensure_chromedriver", return_value=None):
        events = scrape_youthall_events()

    assert events == []


# ── TechCareer ────────────────────────────────────────────────────────────────


def test_techcareer_returns_events():
    from app.scrapers.techcareer_scraper import scrape_techcareer_events

    mock_driver = _make_selenium_driver(_html("techcareer.html"))

    with patch(
        "app.scrapers.techcareer_scraper.ensure_chromedriver",
        return_value="/usr/bin/chromedriver",
    ), patch(
        "app.scrapers.techcareer_scraper.webdriver.Chrome", return_value=mock_driver
    ), patch(
        "app.scrapers.techcareer_scraper.WebDriverWait"
    ), patch(
        "app.scrapers.techcareer_scraper.time.sleep"
    ):
        events = scrape_techcareer_events()

    assert isinstance(events, list)
    assert len(events) >= 1
    assert all("title" in e for e in events)
    assert all("url" in e for e in events)


def test_techcareer_no_chromedriver_returns_empty():
    from app.scrapers.techcareer_scraper import scrape_techcareer_events

    with patch(
        "app.scrapers.techcareer_scraper.ensure_chromedriver", return_value=None
    ):
        events = scrape_techcareer_events()

    assert events == []


# ── Kodluyoruz ────────────────────────────────────────────────────────────────


def test_kodluyoruz_returns_events():
    from app.scrapers.kodluyoruz_scraper import scrape_kodluyoruz_events

    mock_response = MagicMock()
    mock_response.text = _html("kodluyoruz.html")
    mock_response.encoding = "utf-8"

    with patch(
        "app.scrapers.kodluyoruz_scraper.requests.get", return_value=mock_response
    ):
        events = scrape_kodluyoruz_events()

    assert isinstance(events, list)
    assert len(events) >= 1
    assert all("title" in e for e in events)


def test_kodluyoruz_network_error_returns_empty():
    import requests as req
    from app.scrapers.kodluyoruz_scraper import scrape_kodluyoruz_events

    with patch(
        "app.scrapers.kodluyoruz_scraper.requests.get",
        side_effect=req.exceptions.ConnectionError,
    ):
        events = scrape_kodluyoruz_events()

    assert events == []


# ── Anbean ────────────────────────────────────────────────────────────────────


def test_anbean_returns_events():
    from app.scrapers.anbean_scraper import scrape_anbean_events

    mock_response = MagicMock()
    mock_response.content = _html("anbean.html").encode("utf-8")
    mock_response.encoding = "utf-8"

    with patch("app.scrapers.anbean_scraper.requests.get", return_value=mock_response):
        events = scrape_anbean_events()

    assert isinstance(events, list)
    assert len(events) >= 1
    assert all("url" in e for e in events)
