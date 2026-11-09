import re
from datetime import datetime
from typing import Optional

import requests
from bs4 import BeautifulSoup

LIST_URL = "https://www.youthall.com/tr/etkinlikler/"
BASE_URL = "https://www.youthall.com"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; TechEventRadar/1.0)"}

_MONTHS = {
    "oca": 1,
    "şub": 2,
    "mar": 3,
    "nis": 4,
    "may": 5,
    "haz": 6,
    "tem": 7,
    "ağu": 8,
    "eyl": 9,
    "eki": 10,
    "kas": 11,
    "ara": 12,
}
_DAY_MONTH = re.compile(r"(\d{1,2})\s+([^\W\d_]+)", re.UNICODE)


def _day_month(text: str) -> list[tuple[int, int]]:
    """'01 – 02 Aralık' -> [(1, 12), (2, 12)]; '03 Oca – 30 Eyl' -> [(3, 1), (30, 9)].

    A bare day before the range separator ('01 – 02 Aralık') has no month of
    its own and is borrowed from the month that follows.
    """
    text = text.replace("İ", "i").replace("I", "ı").lower()
    found = [
        (int(day), _MONTHS[word[:3]])
        for day, word in _DAY_MONTH.findall(text)
        if word[:3] in _MONTHS
    ]
    days = re.findall(r"\d{1,2}", text)
    if len(found) == 1 and len(days) == 2:
        found.insert(0, (int(days[0]), found[0][1]))
    return found


def _nearest_year(day: int, month: int, now: datetime) -> Optional[datetime]:
    """The listing omits the year; take the year that lands closest to today."""
    best = None
    for year in (now.year - 1, now.year, now.year + 1):
        try:
            candidate = datetime(year, month, day)
        except ValueError:
            continue
        if best is None or abs(candidate - now) < abs(best - now):
            best = candidate
    return best


def _event_end(parts: list[tuple[int, int]], start: datetime) -> datetime:
    """Last day of a range; a range that wraps the year ends in the next one."""
    day, month = parts[-1]
    try:
        end = datetime(start.year, month, day)
    except ValueError:
        return start
    return end if end >= start else end.replace(year=start.year + 1)


def _deadline(day: int, month: int, event_end: datetime) -> Optional[datetime]:
    """A deadline is never after the event ends: use its year, else the year before."""
    for year in (event_end.year, event_end.year - 1):
        try:
            candidate = datetime(year, month, day)
        except ValueError:
            continue
        if candidate <= event_end:
            return candidate
    return None


def _fmt(value: Optional[datetime]) -> Optional[str]:
    return value.strftime("%Y-%m-%d %H:%M:%S") if value else None


def _location(card) -> Optional[str]:
    """With two or more tags the first is the venue/city/'Online', the last the category."""
    tags = [t.get_text(" ", strip=True) for t in card.select(".events-card__tag")]
    return tags[0] if len(tags) >= 2 else None


def parse_youthall_events(html: str, now: Optional[datetime] = None) -> list[dict]:
    now = now or datetime.now()
    soup = BeautifulSoup(html, "html.parser")
    events, seen = [], set()
    for card in soup.select("article.events-card"):
        link = card.select_one("a.events-card__link[href]")
        title = card.select_one(".events-card__title")
        if not link or not title:
            continue
        url = str(link["href"])
        if not url.startswith("http"):
            url = BASE_URL + url
        # The page renders the same cards twice (carousel and list).
        if url in seen:
            continue
        seen.add(url)

        when = card.select_one(".events-card__when .events-card__val")
        start_parts = _day_month(when.get_text(" ", strip=True)) if when else []
        start = _nearest_year(*start_parts[0], now) if start_parts else None

        deadline_el = card.select_one(".events-card__deadline-val")
        deadline_parts = (
            _day_month(deadline_el.get_text(" ", strip=True)) if deadline_el else []
        )
        deadline = (
            _deadline(*deadline_parts[-1], _event_end(start_parts, start))
            if deadline_parts and start
            else None
        )

        img = card.select_one("img.events-card__img")
        events.append(
            {
                "title": title.get_text(" ", strip=True),
                "url": url,
                "date": _fmt(start),
                "application_deadline": _fmt(deadline),
                "description": "Etkinlik açıklaması mevcut değil.",
                "image_url": img.get("src", "") if img else "",
                "source": "Youthall",
                "location": _location(card),
                "is_active": True,
            }
        )
    return events


def scrape_youthall_events() -> list[dict]:
    try:
        response = requests.get(LIST_URL, timeout=30, headers=HEADERS)
        response.raise_for_status()
        response.encoding = "utf-8"
        return parse_youthall_events(response.text)
    except requests.RequestException as exc:
        print(f"Youthall: network error: {exc}")
        raise
