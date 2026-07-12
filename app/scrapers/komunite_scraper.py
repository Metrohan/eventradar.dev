import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

LIST_URL = "https://komunite.com.tr/etkinlikler"
BASE_URL = "https://komunite.com.tr/"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; TechEventRadar/1.0)"}


def parse_komunite_events(html: bytes | str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    events: list[dict] = []
    seen: set[str] = set()
    for link in soup.select('a[href*="/etkinlikler/"]'):
        url = urljoin(BASE_URL, link.get("href", ""))
        if url in seen:
            continue
        card = link.find_parent("div")
        if not card:
            continue
        text = " ".join(card.get_text(" ", strip=True).split())
        if "Yakında Açıklanacak" in text:
            continue
        date_match = re.search(r"(\d{1,2}(?:\s*-\s*\d{1,2})?\s+[A-Za-zÇĞİÖŞÜçğıöşü]+\s+\d{4})(?:\s*\|\s*(\d{1,2}:\d{2}))?", text)
        paragraphs = [node.get_text(" ", strip=True) for node in card.select("p")]
        description = max(paragraphs, key=len, default="")
        title_node = card.select_one("h2, h3, h4")
        title = title_node.get_text(" ", strip=True) if title_node else None
        if not title and description in paragraphs:
            description_index = paragraphs.index(description)
            title = next(
                (
                    value
                    for value in reversed(paragraphs[:description_index])
                    if len(value) > 3
                    and not re.search(r"\d{1,2}:\d{2}|\d{4}", value)
                    and "Komünite Space" not in value
                    and value != "Online"
                ),
                None,
            )
        if not date_match or not title:
            continue
        seen.add(url)
        location = next((value for value in paragraphs if "Komünite Space" in value or value == "Online"), None)
        events.append({
            "title": title,
            "description": description,
            "date": " ".join(part for part in date_match.groups() if part),
            "application_deadline": None,
            "location": location,
            "url": url,
            "image_url": None,
            "source": "Komünite",
            "is_active": True,
        })
    return events


def scrape_komunite_events() -> list[dict]:
    try:
        response = requests.get(LIST_URL, timeout=30, headers=HEADERS)
        response.raise_for_status()
        return parse_komunite_events(response.content)
    except requests.RequestException as exc:
        print(f"Komünite: network error: {exc}")
        return []
