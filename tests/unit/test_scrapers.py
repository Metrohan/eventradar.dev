import json
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


# ── Patika.dev / Skillcamp ───────────────────────────────────────────────────


def test_patika_returns_only_open_unique_programs():
    from app.scrapers.patika_scraper import parse_patika_events

    events = parse_patika_events(_html("patika.html"))

    assert len(events) == 1
    assert events[0]["title"] == "Grid Up Hackathon"
    assert events[0]["application_deadline"] == "8 Ağustos 2026"
    assert events[0]["source"] == "Patika.dev"


def test_patika_enriches_event_from_detail_page():
    from app.scrapers.patika_scraper import scrape_patika_events

    list_response = MagicMock(text=_html("patika.html"))
    list_response.raise_for_status = MagicMock()
    detail_response = MagicMock(text=_html("patika_detail.html"))
    detail_response.raise_for_status = MagicMock()
    with patch(
        "app.scrapers.patika_scraper.requests.get",
        side_effect=[list_response, detail_response],
    ):
        events = scrape_patika_events()

    assert events[0]["date"] == "1/9/2026"
    assert events[0]["location"] == "Online"


# ── Komünite ─────────────────────────────────────────────────────────────────


def test_komunite_deduplicates_responsive_cards_and_skips_unknown_dates():
    from app.scrapers.komunite_scraper import parse_komunite_events

    events = parse_komunite_events(_html("komunite.html"))

    assert len(events) == 1
    assert events[0]["title"] == "Vibe Coding Bootcamp"
    assert events[0]["date"] == "18 - 19 Temmuz 2026 10:00"
    assert events[0]["location"] == "Komünite Space, Vadistanbul"


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


def _mock_detail_response():
    mock_response = MagicMock()
    mock_response.text = _html("techcareer_detail.html")
    mock_response.raise_for_status = MagicMock()
    return mock_response


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
    ), patch(
        "app.scrapers.techcareer_scraper.requests.get",
        return_value=_mock_detail_response(),
    ):
        events = scrape_techcareer_events()

    assert isinstance(events, list)
    assert len(events) >= 1
    assert all("title" in e for e in events)
    assert all("url" in e for e in events)


def test_techcareer_uses_detail_page_date_not_deadline():
    """
    Regression test: liste sayfasındaki "single-event-date" alanı başvuru son
    tarihidir (10.05.2027), gerçek etkinlik tarihi/saati sadece detay
    sayfasındaki "Tarih:" satırında bulunur (15 Mayıs Cumartesi | 14.00-16.00).
    Scraper, "date" alanına deadline'ı değil gerçek etkinlik tarihini yazmalı.
    """
    from datetime import datetime
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
    ), patch(
        "app.scrapers.techcareer_scraper.requests.get",
        return_value=_mock_detail_response(),
    ):
        events = scrape_techcareer_events()

    assert len(events) >= 1
    deadlines = {e["application_deadline"] for e in events}
    assert deadlines == {"10.05.2027", "15.06.2027"}
    for event in events:
        assert isinstance(event["date"], datetime)
        assert event["date"].day == 15
        assert event["date"].hour == 14
        # Kritik regresyon: "date" alanı deadline değerleriyle eşleşmemeli
        assert event["date"].strftime("%d.%m.%Y") not in deadlines
        # Açıklama artık detay sayfasındaki gerçek metinden geliyor,
        # jenerik "TechCareer.net etkinliği" placeholder'ı değil
        assert "Prompt Yazımı Atölyesi" in event["description"]
        assert event["description"] != "TechCareer.net etkinliği"


def test_techcareer_no_chromedriver_returns_empty():
    from app.scrapers.techcareer_scraper import scrape_techcareer_events

    with patch(
        "app.scrapers.techcareer_scraper.ensure_chromedriver", return_value=None
    ):
        events = scrape_techcareer_events()

    assert events == []


# ── Kodluyoruz ────────────────────────────────────────────────────────────────


def _kodluyoruz_get_side_effect(url, *args, **kwargs):
    mock_response = MagicMock()
    mock_response.encoding = "utf-8"
    if url == "https://kodluyoruz.org/programlar":
        mock_response.text = _html("kodluyoruz.html")
    else:
        mock_response.text = _html("kodluyoruz_detail.html")
    return mock_response


def test_kodluyoruz_returns_events():
    from app.scrapers.kodluyoruz_scraper import scrape_kodluyoruz_events

    with patch(
        "app.scrapers.kodluyoruz_scraper.requests.get",
        side_effect=_kodluyoruz_get_side_effect,
    ):
        events = scrape_kodluyoruz_events()

    assert isinstance(events, list)
    assert len(events) >= 1
    assert all("title" in e for e in events)


def test_kodluyoruz_uses_real_detail_page_description():
    """
    Regresyon: liste sayfasındaki '.program-format' alanı sadece 'Ücretsiz'
    gibi bir etikettir; açıklama artık detay sayfasındaki gerçek metinden gelmeli.
    """
    from app.scrapers.kodluyoruz_scraper import scrape_kodluyoruz_events

    with patch(
        "app.scrapers.kodluyoruz_scraper.requests.get",
        side_effect=_kodluyoruz_get_side_effect,
    ):
        events = scrape_kodluyoruz_events()

    assert len(events) >= 1
    for event in events:
        assert "Programın amacı" in event["description"]


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


def _anbean_get_side_effect(url, *args, **kwargs):
    mock_response = MagicMock()
    mock_response.encoding = "utf-8"
    if url.rstrip("/").endswith("/etkinlikler"):
        mock_response.content = _html("anbean.html").encode("utf-8")
    else:
        mock_response.content = _html("anbean_detail.html").encode("utf-8")
    return mock_response


def test_anbean_returns_events():
    from app.scrapers.anbean_scraper import scrape_anbean_events

    with patch(
        "app.scrapers.anbean_scraper.requests.get",
        side_effect=_anbean_get_side_effect,
    ):
        events = scrape_anbean_events()

    assert isinstance(events, list)
    assert len(events) >= 1
    assert all("url" in e for e in events)


def test_anbean_uses_real_detail_page_description():
    """
    Regresyon: description artık sabit 'Anbean Kampüs etkinliği.' placeholder'ı
    değil, detay sayfasındaki gerçek 'Etkinlik Hakkında' metninden gelmeli.
    """
    from app.scrapers.anbean_scraper import scrape_anbean_events

    with patch(
        "app.scrapers.anbean_scraper.requests.get",
        side_effect=_anbean_get_side_effect,
    ):
        events = scrape_anbean_events()

    assert len(events) >= 1
    for event in events:
        assert "Üniversite öğrencileri" in event["description"]


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


# ── Tech Istanbul ────────────────────────────────────────────────────────────


def _techistanbul_mock_response():
    mock_response = MagicMock()
    mock_response.json.return_value = json.loads(_html("techistanbul.json"))
    mock_response.raise_for_status = MagicMock()
    return mock_response


def test_techistanbul_returns_events():
    from app.scrapers.techistanbul_scraper import scrape_techistanbul_events

    with patch(
        "app.scrapers.techistanbul_scraper.requests.get",
        return_value=_techistanbul_mock_response(),
    ):
        events = scrape_techistanbul_events()

    assert isinstance(events, list)
    # 3 etkinlikten biri isActive=false, sadece 2 tanesi dönmeli
    assert len(events) == 2
    assert all("title" in e for e in events)
    assert all("url" in e for e in events)


def test_techistanbul_skips_inactive_events():
    from app.scrapers.techistanbul_scraper import scrape_techistanbul_events

    with patch(
        "app.scrapers.techistanbul_scraper.requests.get",
        return_value=_techistanbul_mock_response(),
    ):
        events = scrape_techistanbul_events()

    titles = [e["title"] for e in events]
    assert "Pasif Etkinlik" not in titles


def test_techistanbul_strips_html_from_description():
    from app.scrapers.techistanbul_scraper import scrape_techistanbul_events

    with patch(
        "app.scrapers.techistanbul_scraper.requests.get",
        return_value=_techistanbul_mock_response(),
    ):
        events = scrape_techistanbul_events()

    canva = next(e for e in events if e["title"] == "Canva 101")
    assert "<p>" not in canva["description"]
    assert "Ücretsiz bir tasarım atölyesi." in canva["description"]


def test_techistanbul_maps_location_and_online():
    from app.scrapers.techistanbul_scraper import scrape_techistanbul_events

    with patch(
        "app.scrapers.techistanbul_scraper.requests.get",
        return_value=_techistanbul_mock_response(),
    ):
        events = scrape_techistanbul_events()

    canva = next(e for e in events if e["title"] == "Canva 101")
    assert canva["location"] == "Küçükçekmece"

    webinar = next(e for e in events if e["title"] == "Online Webinar")
    assert webinar["location"] == "Online"


def test_techistanbul_uses_real_dates_not_none():
    from app.scrapers.techistanbul_scraper import scrape_techistanbul_events
    from app.services.event_ingestion import normalize_date

    with patch(
        "app.scrapers.techistanbul_scraper.requests.get",
        return_value=_techistanbul_mock_response(),
    ):
        events = scrape_techistanbul_events()

    canva = next(e for e in events if e["title"] == "Canva 101")
    parsed = normalize_date(canva["date"])
    assert parsed is not None
    assert parsed.year == 2026
    assert parsed.month == 6
    assert parsed.day == 19
    assert parsed.hour == 13
