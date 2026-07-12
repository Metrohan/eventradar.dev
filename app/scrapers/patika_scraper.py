import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

LIST_URL = "https://www.patika.dev/bootcamp"
BASE_URL = "https://www.patika.dev"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; TechEventRadar/1.0)"}


def _detail_metadata(url: str) -> tuple[str | None, str | None]:
    response = requests.get(url, timeout=20, headers=HEADERS)
    response.raise_for_status()
    text = " ".join(
        BeautifulSoup(response.text, "html.parser").get_text(" ", strip=True).split()
    )
    start = re.search(r"Başlangıç\s+(\d{1,2}/\d{1,2}/\d{4})", text)
    location = re.search(r"Konum\s+(.+?)(?:\s+💰|\s+Başvur|$)", text)
    return (
        start.group(1) if start else None,
        location.group(1).strip() if location else None,
    )


def parse_patika_events(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    events: list[dict] = []
    seen: set[str] = set()
    for card in soup.select('a[href^="/bootcamp/"]'):
        text = " ".join(card.get_text(" ", strip=True).split())
        if "Başvurular Açık" not in text:
            continue
        url = urljoin(BASE_URL, card.get("href", ""))
        title_node = card.select_one("h2, h3")
        if not url or not title_node or url in seen:
            continue
        seen.add(url)
        description_node = card.select_one("p")
        deadline = re.search(r"Son başvuru:\s*(.+?)(?:$|Başvurular)", text)
        image = card.select_one("img[src]")
        events.append(
            {
                "title": title_node.get_text(" ", strip=True),
                "description": (
                    description_node.get_text(" ", strip=True)
                    if description_node
                    else ""
                ),
                "date": None,
                "application_deadline": deadline.group(1).strip() if deadline else None,
                "location": None,
                "url": url,
                "image_url": urljoin(BASE_URL, image.get("src")) if image else None,
                "source": "Patika.dev",
                "is_active": True,
            }
        )
    return events


def scrape_patika_events() -> list[dict]:
    try:
        response = requests.get(LIST_URL, timeout=30, headers=HEADERS)
        response.raise_for_status()
        events = parse_patika_events(response.text)
        for event in events:
            try:
                event["date"], event["location"] = _detail_metadata(event["url"])
            except requests.RequestException:
                pass
        return events
    except requests.RequestException as exc:
        print(f"Patika.dev: network error: {exc}")
        return []
