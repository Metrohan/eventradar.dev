import re
from datetime import datetime

import requests

LIST_URL = "https://komunite.com.tr/etkinlikler"
FEED_URL = "https://komunite.com.tr/etkinlikler/takvim.ics"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; TechEventRadar/1.0)"}


def _unfold(text: str) -> list[str]:
    lines: list[str] = []
    for line in text.splitlines():
        if line[:1] in (" ", "\t") and lines:
            lines[-1] += line[1:]
        else:
            lines.append(line)
    return lines


def _unescape(value: str) -> str:
    return re.sub(r"\\(.)", lambda m: "\n" if m.group(1) in "nN" else m.group(1), value)


def parse_komunite_events(ics: str) -> list[dict]:
    events: list[dict] = []
    seen: set[str] = set()
    fields: dict[str, str] | None = None
    for line in _unfold(ics):
        if line == "BEGIN:VEVENT":
            fields = {}
        elif line == "END:VEVENT" and fields is not None:
            event = _to_event(fields)
            if event and event["url"] not in seen:
                seen.add(event["url"])
                events.append(event)
            fields = None
        elif fields is not None and ":" in line:
            name, _, value = line.partition(":")
            fields[name.split(";")[0]] = value
    return events


def _to_event(fields: dict[str, str]) -> dict | None:
    url = fields.get("URL")
    title = _unescape(fields.get("SUMMARY", "")).strip()
    try:
        start = datetime.strptime(fields.get("DTSTART", ""), "%Y%m%dT%H%M%S")
    except ValueError:
        return None
    if not url or not title:
        return None
    description = _unescape(fields.get("DESCRIPTION", "")).split("\n\n")[0].strip()
    return {
        "title": title,
        "description": description,
        "date": start,
        "application_deadline": None,
        "location": _unescape(fields.get("LOCATION", "")).strip() or None,
        "url": url,
        "image_url": None,
        "source": "Komünite",
        "is_active": True,
    }


def scrape_komunite_events() -> list[dict]:
    try:
        response = requests.get(FEED_URL, timeout=30, headers=HEADERS)
        response.raise_for_status()
        response.encoding = "utf-8"
        return parse_komunite_events(response.text)
    except requests.RequestException as exc:
        print(f"Komünite: network error: {exc}")
        raise
