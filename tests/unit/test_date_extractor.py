import os

os.environ.setdefault("ALLOW_INSECURE_DEFAULTS", "true")
os.environ.setdefault("SECRET_KEY", "test-secret-key-that-is-at-least-32-chars")
os.environ.setdefault("ADMIN_USERNAME", "testadmin")
os.environ.setdefault("ADMIN_PASSWORD", "testpassword")

from datetime import datetime, date
from app.services.date_extractor import extract_date_from_text, parse_event_date


def test_returns_none_for_empty_string():
    assert extract_date_from_text("") is None


def test_returns_none_for_no_date():
    assert extract_date_from_text("Bu metinde tarih yok.") is None


def test_extracts_full_turkish_date():
    result = extract_date_from_text("Etkinlik 15 Mayıs 2027 tarihinde başlıyor.")
    assert isinstance(result, datetime)
    assert result.month == 5
    assert result.day == 15
    assert result.year == 2027


def test_extracts_dotted_date():
    result = extract_date_from_text("Kayıt: 20.06.2027")
    assert isinstance(result, datetime)
    assert result.day == 20
    assert result.month == 6
    assert result.year == 2027


def test_returns_datetime_not_string():
    result = extract_date_from_text("15 Haziran 2027 tarihinde.")
    assert isinstance(result, datetime)


# ─── parse_event_date tests ─────────────────────────────────────────────────


def test_parse_iso_format():
    """ISO 8601: 2026-05-15"""
    dt = parse_event_date("2026-05-15")
    assert isinstance(dt, datetime)
    assert dt.year == 2026
    assert dt.month == 5
    assert dt.day == 15


def test_parse_iso_with_time():
    """ISO 8601 with time: 2026-05-15 14:30:00"""
    dt = parse_event_date("2026-05-15 14:30:00")
    assert isinstance(dt, datetime)
    assert dt.year == 2026
    assert dt.month == 5
    assert dt.day == 15
    assert dt.hour == 14
    assert dt.minute == 30
    assert dt.second == 0


def test_parse_turkish_long():
    """Turkish long format: 15 Mayıs 2026"""
    dt = parse_event_date("15 Mayıs 2026")
    assert isinstance(dt, datetime)
    assert dt.day == 15
    assert dt.month == 5
    assert dt.year == 2026


def test_parse_slash_delimited():
    """Slash-delimited: 15/05/2026"""
    dt = parse_event_date("15/05/2026")
    assert isinstance(dt, datetime)
    assert dt.day == 15
    assert dt.month == 5
    assert dt.year == 2026


def test_parse_dot_delimited():
    """Dot-delimited: 15.05.2026"""
    dt = parse_event_date("15.05.2026")
    assert isinstance(dt, datetime)
    assert dt.day == 15
    assert dt.month == 5
    assert dt.year == 2026


def test_parse_unparseable_returns_none():
    """Unparseable input returns None without raising"""
    assert parse_event_date("") is None
    assert parse_event_date(None) is None
    assert parse_event_date("geçersiz tarih") is None
    assert parse_event_date("abc") is None
    assert parse_event_date(12345) is None


def test_parse_iso_with_slash_separator():
    """ISO-like with slashes: 2026/05/15"""
    dt = parse_event_date("2026/05/15")
    assert isinstance(dt, datetime)
    assert dt.year == 2026
    assert dt.month == 5
    assert dt.day == 15


def test_parse_turkish_month_variants():
    """Turkish month name variants"""
    for month_name in [
        "Ocak",
        "Şubat",
        "Mart",
        "Nisan",
        "Mayıs",
        "Haziran",
        "Temmuz",
        "Ağustos",
        "Eylül",
        "Ekim",
        "Kasım",
        "Aralık",
    ]:
        dt = parse_event_date(f"01 {month_name} 2026")
        assert isinstance(dt, datetime), f"Failed for month: {month_name}"


def test_no_digit_returns_none():
    """Rakam içermeyen metin dateparser'a ulaşmadan None döner."""
    assert parse_event_date("Kayıt Açık") is None
    assert parse_event_date("Başvuru devam ediyor") is None
    assert parse_event_date("Yakında") is None


def test_insane_year_returns_none():
    """Geçmişte veya çok uzakta tarihler kabul edilmez."""
    assert parse_event_date("01.01.1990") is None
    assert parse_event_date("01.01.2099") is None


def test_duplicate_url_in_batch_does_not_crash(test_db):
    """Aynı URL batch içinde iki kez gelirse ikincisi sessizce atlanır."""
    import os
    os.environ.setdefault("ALLOW_INSECURE_DEFAULTS", "true")
    from unittest.mock import patch
    from app.services.scraper_service import process_scraped_events

    events = [
        {"title": "Test", "url": "https://example.com/dup", "date": "01 Ocak 2027", "source": "test"},
        {"title": "Test Dup", "url": "https://example.com/dup", "date": "01 Ocak 2027", "source": "test"},
    ]
    with patch("app.core.database.SessionLocal", return_value=test_db):
        result = process_scraped_events(events, "test")

    assert "New: 1" in result
