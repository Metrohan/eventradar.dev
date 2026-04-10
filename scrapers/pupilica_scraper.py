from datetime import datetime, timedelta
from typing import List, Dict, Any
import requests

API_URL = "https://pupilica.com/api/v2/generic/web_search_read"
DEFAULT_IMAGE = "https://dummyimage.com/1200x630/0b1220/ffffff&text=Pupilica"

def scrape_pupilica_events() -> List[Dict[str, Any]]:
    payload = {
        "meta": {
            "context": {},
            "domain": [],
            "specification": {
                "name": {},
                "date_begin": {},
                "date_end": {},
                "application_start_date": {},
                "application_end_date": {},
                "location": {},
                "meeting_url": {},
                "website_absolute_url": {},
                "publisher_id": {"fields": {"name": {}}},
                "cms_event_type_id": {"fields": {"name": {}}},
                "instructor_ids": {"fields": {"name": {}}}
            },
            "offset": 0,
            "limit": 300,
            "order": None,
            "count_limit": None
        },
        "model": "event.event"
    }

    try:
        r = requests.post(API_URL, json=payload, timeout=30)
        r.raise_for_status()
        records = r.json().get("records", [])
    except Exception as e:
        print(f"Pupilica API error: {e}")
        return []

    now = datetime.utcnow() - timedelta(days=1)
    events = []

    for rec in records:
        date_begin = rec.get("date_begin")
        if not date_begin:
            continue

        try:
            dt = datetime.strptime(date_begin, "%Y-%m-%d %H:%M:%S")
        except Exception:
            continue

        # Geçmişleri at
        if dt < now:
            continue

        title = str(rec.get("name") or "").strip()
        if not title:
            continue

        publisher = (rec.get("publisher_id") or {}).get("name", "")
        event_type = (rec.get("cms_event_type_id") or {}).get("name", "")
        instructors = ", ".join([i.get("name", "") for i in (rec.get("instructor_ids") or []) if i.get("name")])

        desc_parts = [p for p in [event_type, publisher, instructors] if p]
        description = " | ".join(desc_parts) if desc_parts else "Pupilica etkinliği"

        events.append({
            "title": title,
            "description": description,
            "date": dt.strftime("%Y-%m-%d %H:%M:%S"),
            "location": str(rec.get("location") or "Online"),
            "url": str(rec.get("website_absolute_url") or "https://pupilica.com/events"),
            "image_url": f"https://learn.pupilica.com/web/image/event.event/{rec.get('id')}/cover" if rec.get("id") else DEFAULT_IMAGE,
            "source": "Pupilica",
            "is_active": True
        })

    print(f"Pupilica'ten {len(events)} etkinlik çekildi.")
    return events
