import os
import sys
from unittest.mock import MagicMock

os.environ.setdefault("ALLOW_INSECURE_DEFAULTS", "true")
os.environ.setdefault("SECRET_KEY", "test-secret-key-that-is-at-least-32-chars")
os.environ.setdefault("ADMIN_USERNAME", "testadmin")
os.environ.setdefault("ADMIN_PASSWORD", "testpassword")

# undetected_chromedriver uses distutils which is removed in Python 3.12+.
# Mock the package before any app imports that trigger it at module level.
_uc_mock = MagicMock()
_uc_mock.ChromeOptions = MagicMock
_uc_mock.Chrome = MagicMock
sys.modules.setdefault("undetected_chromedriver", _uc_mock)

from pathlib import Path
from unittest.mock import patch
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


def test_youthall_defaults_location_to_none_when_venue_unknown():
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

    # Neither fixture card matches the "<date>, <time> <venue>" pattern nor
    # mentions "Online" explicitly, so venue extraction genuinely fails here.
    assert all(e["location"] is None for e in events)


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


# ── Akbank ────────────────────────────────────────────────────────────────────


def test_akbank_parses_event_titles():
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(_html("akbank.html"), "html.parser")
    container = soup.find("div", id="event-list-all")
    assert container is not None
    cards = container.find_all("div", class_="event-item")
    assert len(cards) == 3
    titles = [c.find("h6", class_="text-primary").get_text(strip=True) for c in cards]
    assert "Python Bootcamp İstanbul" in titles
    assert "UI/UX Tasarım Atölyesi" in titles
    assert "Yazılım Kariyeri Semineri" in titles


def test_akbank_parses_date_from_data_attribute():
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(_html("akbank.html"), "html.parser")
    card = soup.find("div", class_="event-item")
    assert card is not None
    assert card.get("data-startdate") == "2027-06-15T10:00:00Z"


def test_akbank_parses_location_from_info_list():
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(_html("akbank.html"), "html.parser")
    card = soup.find("div", class_="event-item")
    info_list = card.find("div", class_="info-list")
    event_info_map = {}
    for row in info_list.find_all("div", class_="d-flex"):
        spans = row.find_all("span")
        if len(spans) >= 3:
            label = spans[0].get_text(strip=True).replace(":", "")
            value = spans[2].get_text(strip=True)
            event_info_map[label] = value
    assert event_info_map.get("Etkinlik Yeri") == "İstanbul"


@patch("undetected_chromedriver.Chrome")
def test_akbank_scraper_returns_list(mock_chrome):
    from app.scrapers.akbank_scraper import scrape_akbank_events

    mock_driver = _make_selenium_driver(_html("akbank.html"))
    mock_chrome.return_value = mock_driver

    with patch(
        "app.scrapers.cs_scraper.get_chrome_options", return_value=MagicMock()
    ), patch("selenium.webdriver.support.ui.WebDriverWait"):
        result = scrape_akbank_events()

    assert isinstance(result, list)


@patch("undetected_chromedriver.Chrome")
def test_akbank_defaults_location_to_none_when_venue_unknown(mock_chrome):
    from app.scrapers.akbank_scraper import scrape_akbank_events

    mock_driver = _make_selenium_driver(_html("akbank.html"))
    mock_chrome.return_value = mock_driver

    with patch(
        "app.scrapers.cs_scraper.get_chrome_options", return_value=MagicMock()
    ), patch("selenium.webdriver.support.ui.WebDriverWait"):
        result = scrape_akbank_events()

    event = next(e for e in result if e["title"] == "Yazılım Kariyeri Semineri")
    assert event["location"] is None


# ── Coderspace ────────────────────────────────────────────────────────────────


def test_cs_scraper_parses_event_cards():
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(_html("cs_scraper.html"), "html.parser")
    cards = soup.select("div.event-card, div.card, article")
    assert len(cards) == 2


def test_cs_scraper_parses_title_and_link():
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(_html("cs_scraper.html"), "html.parser")
    card = soup.select_one("div.event-card")
    assert card is not None
    title = card.select_one("h3, h2, h4")
    assert title is not None
    assert title.get_text(strip=True) == "Machine Learning Summit"
    link = card.select_one("a[href]")
    assert link is not None
    assert "ml-summit" in str(link["href"])


def test_cs_scraper_builds_absolute_url():
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(_html("cs_scraper.html"), "html.parser")
    cards = soup.select("div.event-card")
    urls = []
    for card in cards:
        link = card.select_one("a[href]")
        href = str(link["href"])
        urls.append(href if href.startswith("http") else f"https://coderspace.io{href}")
    assert urls[0] == "https://coderspace.io/etkinlikler/ml-summit"
    assert urls[1] == "https://coderspace.io/etkinlikler/full-stack"


@patch("undetected_chromedriver.Chrome")
def test_cs_scraper_returns_list(mock_chrome):
    from app.scrapers.cs_scraper import scrape_coderspace_events

    mock_driver = _make_selenium_driver(_html("cs_scraper.html"))
    mock_chrome.return_value = mock_driver

    with patch("app.scrapers.cs_scraper.time.sleep"):
        result = scrape_coderspace_events()

    assert isinstance(result, list)


# ── Pupilica ──────────────────────────────────────────────────────────────────


def test_pupilica_parses_cards():
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(_html("pupilica.html"), "html.parser")
    cards = soup.select("div[class*='EventsCard__CardWrapper']")
    assert len(cards) == 2


def test_pupilica_parses_title():
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(_html("pupilica.html"), "html.parser")
    card = soup.select_one("div[class*='EventsCard__CardWrapper']")
    assert card is not None
    h3 = card.find("h3")
    assert h3 is not None
    assert h3.get_text(strip=True) == "Veri Bilimi Bootcamp"


def test_pupilica_parses_date_and_deadline():
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(_html("pupilica.html"), "html.parser")
    card = soup.select_one("div[class*='EventsCard__CardWrapper']")
    all_spans = card.find_all("span")
    date_text = ""
    deadline = ""
    for i, span in enumerate(all_spans):
        text = span.get_text(strip=True)
        if "Tarih" in text and i + 1 < len(all_spans):
            date_text = all_spans[i + 1].get_text(strip=True)
        elif "Son Başvuru" in text and i + 1 < len(all_spans):
            deadline = all_spans[i + 1].get_text(strip=True)
    assert date_text == "10 Haziran 2027"
    assert deadline == "01 Haziran 2027"


def test_pupilica_parses_link():
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(_html("pupilica.html"), "html.parser")
    card = soup.select_one("div[class*='EventsCard__CardWrapper']")
    a_tag = card.find("a", href=True)
    assert a_tag is not None
    url = "https://pupilica.com" + str(a_tag["href"])
    assert url == "https://pupilica.com/events/data-science-bootcamp"


@patch("undetected_chromedriver.Chrome")
def test_pupilica_scraper_returns_list(mock_chrome):
    from app.scrapers.pupilica_scraper import scrape_pupilica_events

    mock_driver = _make_selenium_driver(_html("pupilica.html"))
    mock_chrome.return_value = mock_driver

    with patch(
        "app.scrapers.cs_scraper.get_chrome_options", return_value=MagicMock()
    ), patch("selenium.webdriver.support.ui.WebDriverWait"):
        result = scrape_pupilica_events()

    assert isinstance(result, list)
