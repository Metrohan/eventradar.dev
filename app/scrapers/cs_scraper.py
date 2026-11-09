import logging
import time
from datetime import datetime
from typing import List, Dict, Any, Optional

import requests
from bs4 import BeautifulSoup, Tag
import undetected_chromedriver as uc

logger = logging.getLogger(__name__)

_MONTH_TR = {
    "ocak": 1,
    "subat": 2,
    "mart": 3,
    "nisan": 4,
    "mayis": 5,
    "haziran": 6,
    "temmuz": 7,
    "agustos": 8,
    "eylul": 9,
    "ekim": 10,
    "kasim": 11,
    "aralik": 12,
    "şubat": 2,
    "mayıs": 5,
    "ağustos": 8,
    "eylül": 9,
    "kasım": 11,
    "aralık": 12,
}


def _parse_tr_date(date_str: str, prefer_future: bool = False) -> Optional[datetime]:
    """
    '12 Temmuz' veya '12 Temmuz 2026' gibi Türkçe tarihi parse eder.
    prefer_future=True: yil yoksa ve tarih gecmisteyse bir sonraki yila atar.
    prefer_future=False: yil yoksa her zaman mevcut yili kullanir (deadline filtresi icin).
    """
    if not date_str:
        return None
    parts = date_str.strip().lower().split()
    if len(parts) < 2:
        return None
    try:
        day = int(parts[0])
        month = _MONTH_TR.get(parts[1])
        if not month:
            return None
        year = int(parts[2]) if len(parts) >= 3 else datetime.now().year
        dt = datetime(year, month, day)
        if prefer_future and len(parts) < 3 and dt < datetime.now():
            dt = dt.replace(year=dt.year + 1)
        return dt
    except (ValueError, TypeError):
        return None


def get_chrome_options() -> uc.ChromeOptions:
    options = uc.ChromeOptions()
    options.add_argument("--headless=old")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--blink-settings=imagesEnabled=false")
    return options


LIST_URL = "https://coderspace.io/etkinlikler"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; TechEventRadar/1.0)"}
_DATE_LABELS = ("Son Başvuru", "Başlangıç", "Bitiş")


def parse_coderspace_events(
    html: str, now: Optional[datetime] = None
) -> List[Dict[str, Any]]:
    """Parse the server-rendered list; closed applications are dropped."""
    now = now or datetime.now()
    soup = BeautifulSoup(html, "html.parser")
    events: List[Dict[str, Any]] = []
    seen: set[str] = set()
    past_heading = soup.find(["h2", "h3"], string="Geçmiş etkinlikler")
    past_section = past_heading.find_parent("section") if past_heading else None
    for image_link in soup.select('a[href^="/etkinlikler/"]'):
        img = image_link.find("img")
        card = image_link.parent
        href = str(image_link.get("href", ""))
        if not isinstance(img, Tag) or card is None or href in seen:
            continue
        if past_section is not None and any(
            parent is past_section for parent in image_link.parents
        ):
            continue
        title_link = card.select_one("a.line-clamp-2") or card.select_one("h5 a")
        title = (
            title_link.get_text(strip=True)
            if title_link
            else str(img.get("alt", "")).strip()
        )
        if not title:
            continue

        date_map: Dict[str, str] = {}
        for label_node in card.find_all("span", string=lambda v: v in _DATE_LABELS):
            value = label_node.find_next_sibling("span")
            if value:
                date_map[label_node.get_text(strip=True)] = value.get_text(strip=True)

        # prefer_future=False: a year-less past date must stay in the past.
        deadline_str = date_map.get("Son Başvuru") or date_map.get("Bitiş")
        deadline = _parse_tr_date(deadline_str) if deadline_str else None
        if deadline and deadline < now:
            continue

        date_val = None
        for label in ("Bitiş", "Başlangıç", "Son Başvuru"):
            if label in date_map:
                date_val = _parse_tr_date(date_map[label], prefer_future=True)
                if date_val:
                    break

        seen.add(href)
        description_node = card.select_one("p")
        type_node = card.select_one("span.inline-flex")
        src = str(img.get("src", ""))
        events.append(
            {
                "title": title,
                "url": f"https://coderspace.io{href}",
                # ISO, not "%B": the month name follows the process locale and an
                # English "November" is not understood by parse_event_date.
                "date": date_val.strftime("%Y-%m-%d %H:%M:%S") if date_val else None,
                "application_deadline": (
                    deadline.strftime("%Y-%m-%d %H:%M:%S") if deadline else None
                ),
                "description": (
                    description_node.get_text(strip=True) if description_node else ""
                )
                or f"Coderspace {type_node.get_text(strip=True) if type_node else ''} etkinligi.",
                "image_url": (
                    src if src.startswith("http") else f"https://coderspace.io{src}"
                ),
                "source": "Coderspace",
                "location": "Online",
                "is_active": True,
            }
        )
    return events


def scrape_coderspace_events() -> List[Dict[str, Any]]:
    try:
        response = requests.get(LIST_URL, timeout=30, headers=HEADERS)
        response.raise_for_status()
        response.encoding = "utf-8"
        return parse_coderspace_events(response.text)
    except requests.RequestException as exc:
        logger.error("Coderspace: network error: %s", exc)
        raise
