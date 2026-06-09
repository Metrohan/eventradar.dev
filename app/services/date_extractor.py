import re
from datetime import datetime, date
from dateparser import parse as dateparser_parse
from typing import Optional

_MIN_YEAR = 2015
_MAX_YEAR_OFFSET = 4  # now + 4 years


def _in_sane_range(dt: datetime) -> bool:
    return _MIN_YEAR <= dt.year <= datetime.now().year + _MAX_YEAR_OFFSET


def extract_date_from_text(text: str) -> Optional[datetime]:
    """
    Metin içinden ilk geçerli tarihi döndürür.
    """
    if not text:
        return None
    # Basit tarih regex: 12 Aralık 2025, 13 Mart, 07 Aralık, vs.
    patterns = [
        r"\b\d{1,2} [A-Za-zÇĞİÖŞÜçğıöşü]+ \d{4}\b",  # 12 Aralık 2025
        r"\b\d{1,2} [A-Za-zÇĞİÖŞÜçğıöşü]+\b",  # 13 Mart
        r"\b\d{1,2}\.\d{1,2}\.\d{4}\b",  # 12.12.2025
        r"\b\d{1,2}/\d{1,2}/\d{4}\b",  # 12/12/2025
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            dt = dateparser_parse(match.group(), languages=["tr"])
            if dt:
                return dt
    return None


def parse_event_date(raw: str) -> Optional[datetime]:
    """
    Bir tarih/metin string'ini datetime'a çevirir.

    Desteklenen formatlar:
      - ISO 8601:           "2026-05-15", "2026-05-15 14:30:00"
      - Türkçe uzun:        "15 Mayıs 2026", "15 Mayıs 2026 14:00"
      - Nokta ayraçlı:      "15.05.2026", "15.05.2026 14:30"
      - Slash ayraçlı:      "15/05/2026", "15/05/2026 14:30"

    Parse edilemeyen girdilerde hata fırlatmaz, None döndürür.
    """
    if not raw or not isinstance(raw, str):
        return None

    text = raw.strip()
    if not text:
        return None

    # Rakam içermeyen metin gerçek tarih olamaz; dateparser'a verme
    if not re.search(r"\d", text):
        return None

    # ISO format: 2026-05-15 veya 2026-05-15 14:30:00
    iso_match = re.match(
        r"^(\d{4})[-\/](\d{2})[-\/](\d{2})(?:\s+(\d{1,2}):(\d{2})(?::(\d{2}))?)?$",
        text,
    )
    if iso_match:
        try:
            dt = datetime(
                int(iso_match.group(1)),
                int(iso_match.group(2)),
                int(iso_match.group(3)),
                int(iso_match.group(4) or 0),
                int(iso_match.group(5) or 0),
                int(iso_match.group(6) or 0),
            )
            if _in_sane_range(dt):
                return dt
        except ValueError:
            pass

    # DMY format: 15/05/2026, 15.05.2026, 15-05-2026
    dmy_match = re.match(
        r"^(\d{1,2})[\.\/\-](\d{1,2})[\.\/\-](\d{4})(?:\s+(\d{1,2}):(\d{2})(?::(\d{2}))?)?$",
        text,
    )
    if dmy_match:
        try:
            dt = datetime(
                int(dmy_match.group(3)),
                int(dmy_match.group(2)),
                int(dmy_match.group(1)),
                int(dmy_match.group(4) or 0),
                int(dmy_match.group(5) or 0),
                int(dmy_match.group(6) or 0),
            )
            if _in_sane_range(dt):
                return dt
        except ValueError:
            pass

    # Turkish long format: "15 Mayıs 2026", "15 Mayıs 2026 14:00"
    # Try dateparser for natural language dates
    try:
        dt = dateparser_parse(
            text,
            languages=["tr"],
            settings={
                "DATE_ORDER": "DMY",
                "TIMEZONE": "UTC",
                "RETURN_AS_TIMEZONE_AWARE": False,
                "PREFER_DAY_OF_MONTH": "first",
            },
        )
        if dt and _in_sane_range(dt):
            return dt
    except Exception:
        pass

    # Fallback: strptime denemeleri
    for fmt in (
        "%d.%m.%Y %H:%M:%S",
        "%d.%m.%Y %H:%M",
        "%d.%m.%Y",
        "%d/%m/%Y %H:%M:%S",
        "%d/%m/%Y %H:%M",
        "%d/%m/%Y",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
    ):
        try:
            dt = datetime.strptime(text, fmt)
            if _in_sane_range(dt):
                return dt
        except ValueError:
            continue

    return None
