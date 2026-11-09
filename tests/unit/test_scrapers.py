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

from datetime import datetime
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


def test_komunite_parses_calendar_feed():
    from app.scrapers.komunite_scraper import parse_komunite_events

    events = parse_komunite_events(_html("komunite.ics"))

    assert len(events) == 9
    leadership = next(e for e in events if e["title"] == "AIx Leadership Bootcamp")
    assert leadership["date"] == datetime(2026, 11, 5, 9, 30)
    assert (
        leadership["url"]
        == "https://komunite.com.tr/etkinlikler/aix-leadership-bootcamp"
    )
    assert leadership["location"].startswith("Komünite Space, Ayazağa")
    assert "https://" not in leadership["description"]
    assert leadership["source"] == "Komünite"


def test_komunite_feed_skips_entries_without_url_or_valid_start():
    from app.scrapers.komunite_scraper import parse_komunite_events

    feed = (
        "BEGIN:VEVENT\nSUMMARY:A\nDTSTART;TZID=Europe/Istanbul:bozuk\n"
        "URL:https://komunite.com.tr/etkinlikler/a\nEND:VEVENT\n"
        "BEGIN:VEVENT\nSUMMARY:B\nDTSTART;TZID=Europe/Istanbul:20261105T093000\nEND:VEVENT\n"
    )

    assert parse_komunite_events(feed) == []


def test_patika_decodes_utf8_when_server_sends_no_charset():
    import requests
    from app.scrapers.patika_scraper import scrape_patika_events

    def charsetless(name: str) -> requests.Response:
        response = requests.Response()
        response.status_code = 200
        response.headers["content-type"] = "text/html"
        response._content = _html(name).encode("utf-8")
        # What requests derives from a text/* header without a charset.
        response.encoding = "ISO-8859-1"
        return response

    response, detail = charsetless("patika.html"), charsetless("patika_detail.html")
    with patch(
        "app.scrapers.patika_scraper.requests.get", side_effect=[response, detail]
    ):
        events = scrape_patika_events()

    assert [e["title"] for e in events] == ["Grid Up Hackathon"]
    assert events[0]["date"] == "1/9/2026"


# ── Youthall ──────────────────────────────────────────────────────────────────


def _youthall():
    from app.scrapers.youthall_scraper import parse_youthall_events

    return {
        e["title"]: e
        for e in parse_youthall_events(
            _html("youthall_cards.html"), now=datetime(2026, 11, 10)
        )
    }


def test_youthall_parses_cards_and_drops_duplicates():
    events = _youthall()
    assert len(events) == 5  # fixture repeats its first card
    assert events["AI & Data Career Summit"]["url"] == (
        "https://www.youthall.com/tr/etkinlikler/ai-data-career-summit/"
    )


def test_youthall_extracts_start_date_and_deadline():
    event = _youthall()["AI & Data Career Summit"]
    assert event["date"] == "2026-11-12 00:00:00"
    assert event["application_deadline"] == "2026-11-12 00:00:00"


def test_youthall_range_uses_first_day_and_deadline_before_event():
    events = _youthall()
    assert (
        events["Engineering Career Summit (Fiziksel)"]["date"] == "2026-12-01 00:00:00"
    )
    assert events["Water AI Hackathon 2026"]["date"] == "2026-12-05 00:00:00"
    assert (
        events["Water AI Hackathon 2026"]["application_deadline"]
        == "2026-10-30 00:00:00"
    )


def test_youthall_deadline_may_fall_on_last_day_of_a_range():
    # "01 – 02 Aralık" with deadline "02 Aralık": the deadline is the event's
    # last day, not a year earlier.
    event = _youthall()["Engineering Career Summit (Fiziksel)"]
    assert event["application_deadline"] == "2026-12-02 00:00:00"


def test_youthall_year_rolls_forward_for_next_year_start():
    # "03 Oca – 30 Eyl" listed in November: January means next year, the
    # October deadline stays in the past.
    event = _youthall()["Akbank Fellowship Programı"]
    assert event["date"] == "2027-01-03 00:00:00"
    assert event["application_deadline"] == "2026-10-10 00:00:00"


def test_youthall_location_is_first_tag_unless_only_category():
    events = _youthall()
    assert events["AI & Data Career Summit"]["location"] == "Online"
    assert events["Engineering Career Summit (Fiziksel)"]["location"] == "İstanbul"
    assert events["Water AI Hackathon 2026"]["location"] is None


def test_youthall_unparseable_date_stays_empty():
    from app.scrapers.youthall_scraper import parse_youthall_events

    html = _html("youthall_cards.html").replace("12 Kasım", "Yakında")
    events = parse_youthall_events(html, now=datetime(2026, 11, 10))
    first = next(e for e in events if e["title"] == "AI & Data Career Summit")
    assert first["date"] is None
    assert first["application_deadline"] is None


def test_youthall_network_error_raises():
    import requests
    from app.scrapers.youthall_scraper import scrape_youthall_events

    with patch(
        "app.scrapers.youthall_scraper.requests.get",
        side_effect=requests.ConnectionError("down"),
    ):
        with pytest.raises(requests.ConnectionError):
            scrape_youthall_events()


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


def test_techcareer_no_chromedriver_raises_failure():
    from app.scrapers.techcareer_scraper import scrape_techcareer_events

    with patch(
        "app.scrapers.techcareer_scraper.ensure_chromedriver", return_value=None
    ):
        with pytest.raises(RuntimeError, match="ChromeDriver unavailable"):
            scrape_techcareer_events()


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


def test_kodluyoruz_network_error_reaches_coordinator():
    import requests as req
    from app.scrapers.kodluyoruz_scraper import scrape_kodluyoruz_events

    with patch(
        "app.scrapers.kodluyoruz_scraper.requests.get",
        side_effect=req.exceptions.ConnectionError,
    ):
        with pytest.raises(req.exceptions.ConnectionError):
            scrape_kodluyoruz_events()


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


def test_coderspace_parses_upcoming_cards_and_skips_past_section():
    from app.scrapers.cs_scraper import parse_coderspace_events

    events = parse_coderspace_events(
        _html("coderspace_list.html"), now=datetime(2026, 11, 3)
    )

    titles = [e["title"] for e in events]
    assert titles[:3] == [
        "Data Science & AI Day",
        "49W x Coderspace: Yapay Zeka Paneli",
        "Boğaziçi Teknoloji Zirvesi",
    ]
    assert "Grid Up Datathon" not in titles  # lives under "Geçmiş etkinlikler"
    first = events[0]
    assert first["url"] == "https://coderspace.io/etkinlikler/data-science-ai-day/"
    assert first["date"] == "2026-11-19 00:00:00"  # ISO, independent of locale
    assert first["application_deadline"] == "2026-11-18 00:00:00"
    assert first["source"] == "Coderspace"


def test_coderspace_date_is_understood_by_ingestion_whatever_the_locale():
    from app.scrapers.cs_scraper import parse_coderspace_events
    from app.services.event_ingestion import normalize_date

    events = parse_coderspace_events(
        _html("coderspace_list.html"), now=datetime(2026, 11, 3)
    )
    dated = [e for e in events if e["date"]]
    assert dated
    assert all(normalize_date(e["date"]) is not None for e in dated)
    assert all(normalize_date(e["application_deadline"]) is not None for e in dated)


def test_coderspace_card_without_date_labels_stays_undated():
    from app.scrapers.cs_scraper import parse_coderspace_events

    events = parse_coderspace_events(
        _html("coderspace_list.html"), now=datetime(2026, 11, 3)
    )
    card = next(e for e in events if e["title"].startswith("Vodafone Business"))
    assert card["date"] is None and card["application_deadline"] is None


def test_coderspace_drops_events_whose_application_is_closed():
    from app.scrapers.cs_scraper import parse_coderspace_events

    events = parse_coderspace_events(
        _html("coderspace_list.html"), now=datetime(2026, 12, 30)
    )

    assert [e["title"] for e in events] == [
        "Vodafone Business & İTÜ Siber Güvenlik Akademisi"
    ]  # only the undated card remains


def test_coderspace_scrape_uses_plain_http_and_utf8():
    import requests
    from app.scrapers.cs_scraper import scrape_coderspace_events

    response = requests.Response()
    response.status_code = 200
    response.headers["content-type"] = "text/html"
    response._content = _html("coderspace_list.html").encode("utf-8")
    response.encoding = "ISO-8859-1"
    with patch("app.scrapers.cs_scraper.requests.get", return_value=response):
        events = scrape_coderspace_events()

    assert any(e["title"] == "Boğaziçi Teknoloji Zirvesi" for e in events)


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


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("10 Kasım 2026", "10 Kasım 2026"),
        ("11 Kasım 2026 - 12 Kasım 2026", "11 Kasım 2026"),
        ("23 Kasım 2026 – 2 Aralık 2026", "23 Kasım 2026"),
        ("", ""),
    ],
)
def test_pupilica_range_start(raw, expected):
    from app.scrapers.pupilica_scraper import _range_start

    assert _range_start(raw) == expected


@patch("undetected_chromedriver.Chrome")
def test_pupilica_multi_day_events_get_start_date(mock_chrome):
    from app.scrapers.pupilica_scraper import scrape_pupilica_events
    from app.services.event_ingestion import normalize_date

    mock_chrome.return_value = _make_selenium_driver(_html("pupilica_range.html"))

    with patch(
        "app.scrapers.cs_scraper.get_chrome_options", return_value=MagicMock()
    ), patch("selenium.webdriver.support.ui.WebDriverWait"):
        events = {e["title"]: e for e in scrape_pupilica_events()}

    assert normalize_date(events["Büyük Veri Temelleri"]["date"]) == datetime(
        2026, 11, 10
    )
    assert normalize_date(events["Temel Excel"]["date"]) == datetime(2026, 11, 11)
    assert normalize_date(events["Generative AI Temelleri"]["date"]) == datetime(
        2026, 11, 23
    )


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
