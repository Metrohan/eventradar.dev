# Category / Tag System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add automatic keyword-based category tagging to events, expose it via the API, and let users filter by colorful badges on the homepage.

**Architecture:** Many-to-many `Tag` ↔ `Event` via `event_tags` association table. `TagService.classify_event()` runs on each scrape. `EventResponse` serializes tags as `list[str]`. Frontend renders a `TagBadge` component in both the filter row and on event cards.

**Tech Stack:** SQLAlchemy (many-to-many relationship), Pydantic v2 field_validator, FastAPI Query param, React state + inline styles

---

## File Map

| Action | Path |
|--------|------|
| Create | `app/models/tag.py` |
| Modify | `app/models/event.py` |
| Modify | `app/models/__init__.py` |
| Modify | `tests/conftest.py` |
| Create | `app/services/tag_service.py` |
| Create | `tests/unit/test_tag_service.py` |
| Modify | `app/services/event_service.py` |
| Modify | `tests/unit/test_event_service.py` |
| Modify | `app/schemas/event.py` |
| Modify | `app/api/public.py` |
| Modify | `tests/integration/test_api_public.py` |
| Modify | `app/main.py` |
| Modify | `app/services/scraper_service.py` |
| Create | `scripts/backfill_tags.py` |
| Create | `frontend/src/components/TagBadge.jsx` |
| Modify | `frontend/src/pages/HomePage.jsx` |
| Modify | `frontend/src/components/EventCard.jsx` |

---

### Task 1: Tag model and association table

**Files:**
- Create: `app/models/tag.py`
- Modify: `app/models/event.py`
- Modify: `app/models/__init__.py`
- Modify: `tests/conftest.py`

- [ ] **Step 1: Create `app/models/tag.py`**

```python
from sqlalchemy import Column, Integer, String, Table, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from ..core.database import Base

event_tags = Table(
    "event_tags",
    Base.metadata,
    Column("event_id", Integer, ForeignKey("events.id", ondelete="CASCADE")),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE")),
    PrimaryKeyConstraint("event_id", "tag_id"),
)


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    label = Column(String(50), nullable=False)
    color = Column(String(20), nullable=False)

    def __repr__(self):
        return f"<Tag {self.name}>"
```

- [ ] **Step 2: Add `tags` relationship to `app/models/event.py`**

Add these two imports at the top of the existing imports block:
```python
from sqlalchemy.orm import relationship
```

Then add one line to the `Event` class body, after the `scraped_at` column:
```python
    tags = relationship("Tag", secondary="event_tags", lazy="selectin")
```

The complete updated `Event` class looks like:
```python
class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    date = Column(DateTime)
    location = Column(String(255))
    url = Column(String(500), unique=True, nullable=False, index=True)
    image_url = Column(String(500))
    source = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    scraped_at = Column(DateTime, default=func.now(), nullable=False)
    tags = relationship("Tag", secondary="event_tags", lazy="selectin")

    def __repr__(self):
        return f"<Event {self.title}>"
```

- [ ] **Step 3: Export `Tag` from `app/models/__init__.py`**

Replace the entire file:
```python
from .event import Event
from .announcement import Announcement
from .suggestion import Suggestion
from .event_request import EventRequest
from .pending_event import PendingEvent
from .similar_event_pair import SimilarEventPair
from .scraper_log import ScraperLog
from .subscriber import Subscriber
from .traffic_log import TrafficLog
from .tag import Tag, event_tags

__all__ = [
    "Event",
    "Announcement",
    "Suggestion",
    "EventRequest",
    "PendingEvent",
    "SimilarEventPair",
    "ScraperLog",
    "Subscriber",
    "TrafficLog",
    "Tag",
    "event_tags",
]
```

- [ ] **Step 4: Register Tag model in `tests/conftest.py`**

Add one import line after the existing model imports (around line 21):
```python
import app.models.tag  # noqa: F401
```

- [ ] **Step 5: Verify tables are created in tests**

Run:
```bash
pytest tests/unit/test_event_service.py -v
```
Expected: all existing tests PASS (confirms `Base.metadata.create_all` picks up the new tables without breaking anything).

- [ ] **Step 6: Commit**

```bash
git add app/models/tag.py app/models/event.py app/models/__init__.py tests/conftest.py
git commit -m "feat: add Tag model and event_tags many-to-many association"
```

---

### Task 2: TagService — classify and seed

**Files:**
- Create: `app/services/tag_service.py`
- Create: `tests/unit/test_tag_service.py`

- [ ] **Step 1: Write the failing tests in `tests/unit/test_tag_service.py`**

```python
import os
os.environ.setdefault("ALLOW_INSECURE_DEFAULTS", "true")
os.environ.setdefault("SECRET_KEY", "test-secret-key-that-is-at-least-32-chars")
os.environ.setdefault("ADMIN_USERNAME", "testadmin")
os.environ.setdefault("ADMIN_PASSWORD", "testpassword")

import pytest
from app.services.tag_service import classify_event, seed_tags
from app.models.tag import Tag


def test_classify_hackathon():
    assert "hackathon" in classify_event("İstanbul Hackathon 2026", None)


def test_classify_seminer():
    assert "seminer" in classify_event("Python Webinar Başlıyor", "Online etkinlik")


def test_classify_atolye():
    assert "atolye" in classify_event("React Workshop İstanbul", None)


def test_classify_konferans():
    assert "konferans" in classify_event("Tech Summit Ankara", "Yıllık konferans")


def test_classify_bootcamp():
    assert "bootcamp" in classify_event("Fullstack Bootcamp", None)


def test_classify_multi():
    result = classify_event("Hackathon & Workshop", None)
    assert "hackathon" in result
    assert "atolye" in result


def test_classify_fallback_to_diger():
    result = classify_event("Tanışma Toplantısı", None)
    assert result == ["diger"]


def test_classify_case_insensitive():
    assert "hackathon" in classify_event("HACKATHON FİNALİ", None)


def test_seed_tags_creates_six_tags(test_db):
    seed_tags(test_db)
    tags = test_db.query(Tag).all()
    assert len(tags) == 6
    names = {t.name for t in tags}
    assert names == {"hackathon", "seminer", "atolye", "konferans", "bootcamp", "diger"}


def test_seed_tags_is_idempotent(test_db):
    seed_tags(test_db)
    seed_tags(test_db)  # second call must not raise or duplicate
    assert test_db.query(Tag).count() == 6
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/unit/test_tag_service.py -v
```
Expected: FAIL with `ModuleNotFoundError: No module named 'app.services.tag_service'`

- [ ] **Step 3: Create `app/services/tag_service.py`**

```python
from sqlalchemy.orm import Session
from ..models.tag import Tag

KEYWORD_MAP = {
    "hackathon": ["hackathon", "hack", "datathon", "ideathon"],
    "seminer":   ["seminer", "webinar", "sunum", "söyleşi", "konuşma"],
    "atolye":    ["atölye", "workshop", "lab", "pratik", "uygulama"],
    "konferans": ["konferans", "summit", "zirve", "conference"],
    "bootcamp":  ["bootcamp", "boot camp", "yoğun eğitim", "kamp"],
}

_SEED_DATA = [
    {"name": "hackathon", "label": "Hackathon",         "color": "blue"},
    {"name": "seminer",   "label": "Seminer / Webinar",  "color": "purple"},
    {"name": "atolye",    "label": "Atölye",             "color": "green"},
    {"name": "konferans", "label": "Konferans",           "color": "orange"},
    {"name": "bootcamp",  "label": "Bootcamp",            "color": "pink"},
    {"name": "diger",     "label": "Diğer",               "color": "gray"},
]


def classify_event(title: str, description: str | None) -> list[str]:
    text = (title + " " + (description or "")).lower()
    matched = [
        name
        for name, keywords in KEYWORD_MAP.items()
        if any(kw in text for kw in keywords)
    ]
    return matched if matched else ["diger"]


def seed_tags(db: Session) -> None:
    existing = {t.name for t in db.query(Tag).all()}
    for data in _SEED_DATA:
        if data["name"] not in existing:
            db.add(Tag(**data))
    db.commit()
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/unit/test_tag_service.py -v
```
Expected: all 10 tests PASS

- [ ] **Step 5: Commit**

```bash
git add app/services/tag_service.py tests/unit/test_tag_service.py
git commit -m "feat: add TagService with keyword classification and seed"
```

---

### Task 3: Database migration

**Files:**
- Auto-generated: `alembic/versions/<hash>_add_tags_many_to_many.py`

- [ ] **Step 1: Generate migration**

```bash
alembic revision --autogenerate -m "add tags many-to-many"
```
Expected: a new file under `alembic/versions/` is created containing `op.create_table("tags", ...)` and `op.create_table("event_tags", ...)`.

- [ ] **Step 2: Apply migration**

```bash
alembic upgrade head
```
Expected: `Running upgrade ... -> <hash>, add tags many-to-many`

- [ ] **Step 3: Commit**

```bash
git add alembic/versions/
git commit -m "feat: alembic migration — add tags and event_tags tables"
```

---

### Task 4: EventService — tag filter in get_events

**Files:**
- Modify: `app/services/event_service.py`
- Modify: `tests/unit/test_event_service.py`

- [ ] **Step 1: Write failing tests — append to `tests/unit/test_event_service.py`**

```python
from app.services.tag_service import seed_tags
from app.models.tag import Tag


def _seed_and_get_tags(db):
    seed_tags(db)
    return {t.name: t for t in db.query(Tag).all()}


def test_get_events_filter_by_single_tag(test_db):
    tags = _seed_and_get_tags(test_db)
    service = EventService(test_db)
    e1 = service.create_event(_create_data(url="https://example.com/hack", title="Hackathon 2026"))
    e2 = service.create_event(_create_data(url="https://example.com/work", title="React Workshop"))
    e1.tags = [tags["hackathon"]]
    e2.tags = [tags["atolye"]]
    test_db.commit()

    result = service.get_events(tags=["hackathon"])
    assert len(result) == 1
    assert result[0].url == "https://example.com/hack"


def test_get_events_filter_by_multiple_tags_uses_or(test_db):
    tags = _seed_and_get_tags(test_db)
    service = EventService(test_db)
    e1 = service.create_event(_create_data(url="https://example.com/hack", title="Hackathon 2026"))
    e2 = service.create_event(_create_data(url="https://example.com/work", title="React Workshop"))
    e3 = service.create_event(_create_data(url="https://example.com/other", title="Toplantı"))
    e1.tags = [tags["hackathon"]]
    e2.tags = [tags["atolye"]]
    e3.tags = [tags["diger"]]
    test_db.commit()

    result = service.get_events(tags=["hackathon", "atolye"])
    urls = {e.url for e in result}
    assert "https://example.com/hack" in urls
    assert "https://example.com/work" in urls
    assert "https://example.com/other" not in urls


def test_get_events_no_tag_filter_returns_all(test_db):
    tags = _seed_and_get_tags(test_db)
    service = EventService(test_db)
    e1 = service.create_event(_create_data(url="https://example.com/a"))
    e2 = service.create_event(_create_data(url="https://example.com/b"))
    e1.tags = [tags["hackathon"]]
    test_db.commit()

    result = service.get_events(tags=None)
    assert len(result) == 2
```

- [ ] **Step 2: Run to verify failure**

```bash
pytest tests/unit/test_event_service.py::test_get_events_filter_by_single_tag -v
```
Expected: FAIL with `TypeError: get_events() got an unexpected keyword argument 'tags'`

- [ ] **Step 3: Update `get_events` in `app/services/event_service.py`**

Add this import at the top of the file (alongside the existing `Event` import):
```python
from ..models.tag import Tag
```

Replace the existing `get_events` method:
```python
    def get_events(self, active_only: bool = True, tags: list[str] | None = None) -> List[Event]:
        """Get all events, optionally filtered by active status and/or tag names."""
        query = self.db.query(Event)
        if active_only:
            query = query.filter(Event.is_active == True)
        if tags:
            query = query.filter(Event.tags.any(Tag.name.in_(tags)))
        return query.order_by(Event.date.desc()).all()
```

- [ ] **Step 4: Run all event_service tests**

```bash
pytest tests/unit/test_event_service.py -v
```
Expected: all tests PASS

- [ ] **Step 5: Commit**

```bash
git add app/services/event_service.py tests/unit/test_event_service.py
git commit -m "feat: support tag filtering in EventService.get_events"
```

---

### Task 5: EventResponse schema + public API endpoint

**Files:**
- Modify: `app/schemas/event.py`
- Modify: `app/api/public.py`
- Modify: `tests/integration/test_api_public.py`

- [ ] **Step 1: Write failing integration test**

Open `tests/integration/test_api_public.py` and append:
```python
from app.services.tag_service import seed_tags
from app.models.tag import Tag as TagModel
from app.models.event import Event as EventModel
from datetime import datetime


def _seed_event_with_title(db, url, title):
    e = EventModel(title=title, url=url, source="test", is_active=True, scraped_at=datetime.now())
    db.add(e)
    db.commit()
    db.refresh(e)
    return e


def test_get_events_tags_in_response(client, test_db):
    seed_tags(test_db)
    tags = {t.name: t for t in test_db.query(TagModel).all()}
    event = _seed_event(test_db)
    event.tags = [tags["hackathon"]]
    test_db.commit()

    resp = client.get("/api/events")
    assert resp.status_code == 200
    events = resp.json()["events"]
    assert len(events) == 1
    assert events[0]["tags"] == ["hackathon"]


def test_get_events_filter_by_tags(client, test_db):
    seed_tags(test_db)
    tags = {t.name: t for t in test_db.query(TagModel).all()}
    e1 = _seed_event_with_title(test_db, url="https://example.com/hack", title="Hackathon 2026")
    e2 = _seed_event_with_title(test_db, url="https://example.com/work", title="Workshop")
    e1.tags = [tags["hackathon"]]
    e2.tags = [tags["atolye"]]
    test_db.commit()

    resp = client.get("/api/events?tags=hackathon")
    assert resp.status_code == 200
    events = resp.json()["events"]
    assert len(events) == 1
    assert events[0]["tags"] == ["hackathon"]
```

- [ ] **Step 2: Run to verify failure**

```bash
pytest tests/integration/test_api_public.py::test_get_events_tags_in_response -v
```
Expected: FAIL — `tags` key missing from response JSON

- [ ] **Step 3: Update `app/schemas/event.py`**

Replace the entire file:
```python
from pydantic import BaseModel, field_validator
from typing import List, Optional
from datetime import datetime


class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    date: Optional[datetime] = None
    location: Optional[str] = None
    url: str
    image_url: Optional[str] = None
    source: str = "Admin"
    is_active: bool = True


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    date: Optional[datetime] = None
    location: Optional[str] = None
    url: Optional[str] = None
    image_url: Optional[str] = None
    source: Optional[str] = None
    is_active: Optional[bool] = None


class EventResponse(EventBase):
    id: int
    scraped_at: datetime
    tags: list[str] = []

    @field_validator("tags", mode="before")
    @classmethod
    def extract_tag_names(cls, v):
        if not v:
            return []
        return [t.name if hasattr(t, "name") else t for t in v]

    class Config:
        from_attributes = True


class EventListResponse(BaseModel):
    events: List[EventResponse]
    total_count: int
    last_updated: Optional[str] = None

    class Config:
        from_attributes = True
```

- [ ] **Step 4: Update `app/api/public.py` — add `tags` query param**

Replace the `get_events` function (lines 17-40):
```python
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query

@router.get("/events", response_model=EventListResponse)
async def get_events(
    active_only: bool = True,
    tags: Optional[List[str]] = Query(default=None),
    db: Session = Depends(get_db),
):
    event_service = EventService(db)

    try:
        events = event_service.get_events(active_only=active_only, tags=tags)
        total_count = event_service.get_total_active_events()
        last_updated_event = event_service.get_last_updated_event()

        last_updated = None
        if last_updated_event:
            last_updated = last_updated_event.scraped_at.isoformat()

        return EventListResponse(
            events=events,  # type: ignore[arg-type]
            total_count=total_count,
            last_updated=last_updated,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading events: {str(e)}")
```

Also add `Query` and `List` to the existing imports at the top of `public.py`:
```python
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
```

- [ ] **Step 5: Run integration tests**

```bash
pytest tests/integration/test_api_public.py -v
```
Expected: all tests PASS

- [ ] **Step 6: Run full test suite**

```bash
pytest -v
```
Expected: all tests PASS

- [ ] **Step 7: Commit**

```bash
git add app/schemas/event.py app/api/public.py tests/integration/test_api_public.py
git commit -m "feat: add tags field to EventResponse and ?tags= filter to GET /events"
```

---

### Task 6: Startup seed + scraper auto-tagging

**Files:**
- Modify: `app/main.py`
- Modify: `app/services/scraper_service.py`

- [ ] **Step 1: Call `seed_tags` in `app/main.py` startup hook**

Replace the `on_startup` function:
```python
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    from .core.database import SessionLocal
    from .services.tag_service import seed_tags
    db = SessionLocal()
    try:
        seed_tags(db)
    finally:
        db.close()
```

- [ ] **Step 2: Integrate `classify_event` into `process_scraped_events`**

Open `app/services/scraper_service.py`. Inside the `process_scraped_events` function, add these two imports right after the existing `from ..models.event import Event` import (around line 178):

```python
    from ..models.tag import Tag
    from .tag_service import classify_event
```

Right after the `existing_map` is built (after line ~189), add:
```python
        all_tags = {t.name: t for t in db.query(Tag).all()}
```

Then in the **new event branch** (after `db.add(new_event)`, before `new_count += 1`):
```python
                    db.flush()  # get new_event.id
                    tag_names = classify_event(
                        data.get("title", ""), data.get("description")
                    )
                    new_event.tags = [all_tags[n] for n in tag_names if n in all_tags]
                    new_count += 1
```

And in the **updated event branch** (after `existing_event.scraped_at = now`, before `updated_count += 1`):
```python
                    tag_names = classify_event(
                        data.get("title", existing_event.title),
                        data.get("description", existing_event.description),
                    )
                    existing_event.tags = [all_tags[n] for n in tag_names if n in all_tags]
                    updated_count += 1
```

The final `process_scraped_events` function body from line 175 should look like:

```python
def process_scraped_events(events_data: List[Dict], source_name: str) -> str:
    """Scrape edilen etkinlikleri veritabanına kaydeder."""
    from ..core.database import SessionLocal
    from ..models.event import Event
    from ..models.tag import Tag
    from .tag_service import classify_event

    db = SessionLocal()
    new_count = 0
    updated_count = 0
    failed_urls = []

    try:
        urls = [d.get("url") for d in events_data if d.get("url")]
        existing_map = {
            e.url: e for e in db.query(Event).filter(Event.url.in_(urls)).all()
        }
        all_tags = {t.name: t for t in db.query(Tag).all()}

        now = datetime.now()
        for data in events_data:
            url = data.get("url")
            if not url:
                continue
            try:
                date_val = normalize_date(data.get("date"))
                existing_event = existing_map.get(url)

                if existing_event:
                    existing_event.title = data.get("title", existing_event.title)
                    existing_event.description = data.get(
                        "description", existing_event.description
                    )
                    if date_val is not None:
                        existing_event.date = date_val  # type: ignore[assignment]
                    existing_event.location = data.get(
                        "location", existing_event.location
                    )
                    existing_event.image_url = data.get(
                        "image_url", existing_event.image_url
                    )
                    existing_event.scraped_at = now  # type: ignore[assignment]
                    tag_names = classify_event(
                        data.get("title", existing_event.title),
                        data.get("description", existing_event.description),
                    )
                    existing_event.tags = [all_tags[n] for n in tag_names if n in all_tags]
                    updated_count += 1
                else:
                    new_event = Event(
                        title=data.get("title"),
                        description=data.get("description"),
                        date=date_val,
                        location=data.get("location"),
                        url=url,
                        image_url=data.get("image_url"),
                        source=data.get("source", source_name),
                        is_active=True,
                        scraped_at=now,
                    )
                    db.add(new_event)
                    db.flush()
                    tag_names = classify_event(
                        data.get("title", ""), data.get("description")
                    )
                    new_event.tags = [all_tags[n] for n in tag_names if n in all_tags]
                    new_count += 1
            except Exception as e_event:
                print(f"Error processing single event ({url}): {e_event}")
                failed_urls.append(url)
                continue

        db.commit()
        result = f"New: {new_count}, Updated: {updated_count}"
        if failed_urls:
            result += f", Failed: {len(failed_urls)}"
        return result
    except Exception as e:
        db.rollback()
        print(f"Error in process_scraped_events: {e}")
        return f"Error: {str(e)}"
    finally:
        db.close()
```

- [ ] **Step 3: Run full test suite**

```bash
pytest -v
```
Expected: all tests PASS

- [ ] **Step 4: Commit**

```bash
git add app/main.py app/services/scraper_service.py
git commit -m "feat: seed tags on startup and auto-tag events during scraping"
```

---

### Task 7: Backfill script for existing events

**Files:**
- Create: `scripts/backfill_tags.py`

- [ ] **Step 1: Create `scripts/backfill_tags.py`**

```python
#!/usr/bin/env python3
"""One-time script to classify and assign tags to all existing events."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("ALLOW_INSECURE_DEFAULTS", "true")

from app.core.database import SessionLocal
from app.models.event import Event
from app.models.tag import Tag
from app.services.tag_service import classify_event, seed_tags


def backfill():
    db = SessionLocal()
    try:
        seed_tags(db)
        all_tags = {t.name: t for t in db.query(Tag).all()}
        events = db.query(Event).all()
        for event in events:
            tag_names = classify_event(event.title, event.description)
            event.tags = [all_tags[n] for n in tag_names if n in all_tags]
        db.commit()
        print(f"Backfilled {len(events)} events.")
    finally:
        db.close()


if __name__ == "__main__":
    backfill()
```

- [ ] **Step 2: Commit**

```bash
git add scripts/backfill_tags.py
git commit -m "feat: add backfill_tags script for existing events"
```

---

### Task 8: Frontend — TagBadge component

**Files:**
- Create: `frontend/src/components/TagBadge.jsx`

- [ ] **Step 1: Create `frontend/src/components/TagBadge.jsx`**

```jsx
import React from 'react'

export const TAG_STYLES = {
  hackathon: { label: 'Hackathon',        emoji: '🏆', bg: 'rgba(56,189,248,0.15)',  color: '#38bdf8', border: 'rgba(56,189,248,0.5)'  },
  seminer:   { label: 'Seminer / Webinar', emoji: '🎓', bg: 'rgba(168,85,247,0.15)', color: '#a855f7', border: 'rgba(168,85,247,0.5)'  },
  atolye:    { label: 'Atölye',            emoji: '🛠', bg: 'rgba(34,197,94,0.15)',  color: '#22c55e', border: 'rgba(34,197,94,0.5)'   },
  konferans: { label: 'Konferans',         emoji: '🎤', bg: 'rgba(251,146,60,0.15)', color: '#fb923c', border: 'rgba(251,146,60,0.5)'  },
  bootcamp:  { label: 'Bootcamp',         emoji: '💻', bg: 'rgba(244,63,94,0.15)',  color: '#f43f5e', border: 'rgba(244,63,94,0.5)'   },
  diger:     { label: 'Diğer',            emoji: '📌', bg: 'rgba(148,163,184,0.15)',color: '#94a3b8', border: 'rgba(148,163,184,0.4)' },
}

const TagBadge = ({ name, selected = false, clickable = false, onClick }) => {
  const s = TAG_STYLES[name] || TAG_STYLES.diger

  return (
    <span
      onClick={clickable ? onClick : undefined}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '3px',
        padding: '3px 8px',
        borderRadius: '6px',
        background: selected ? s.bg.replace('0.15', '0.3') : s.bg,
        border: `1px solid ${selected ? s.color : s.border}`,
        color: s.color,
        fontSize: '0.7rem',
        fontWeight: 700,
        cursor: clickable ? 'pointer' : 'default',
        userSelect: 'none',
        transition: 'all 0.15s ease',
        whiteSpace: 'nowrap',
      }}
    >
      <span>{s.emoji}</span>
      <span>{s.label}</span>
    </span>
  )
}

export default TagBadge
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/TagBadge.jsx
git commit -m "feat: add TagBadge component with color styles"
```

---

### Task 9: Frontend — HomePage tag filter

**Files:**
- Modify: `frontend/src/pages/HomePage.jsx`

- [ ] **Step 1: Add imports and state**

At the top of `HomePage.jsx`, add the `TagBadge` import after the existing imports:
```jsx
import TagBadge, { TAG_STYLES } from '../components/TagBadge'
```

Add `selectedTags` state inside the `HomePage` component, after the existing state declarations:
```jsx
const [selectedTags, setSelectedTags] = React.useState([])
```

- [ ] **Step 2: Add tag toggle handler**

Add this function inside `HomePage`, after `clearFilters`:
```jsx
const toggleTag = (name) => {
  setSelectedTags(prev =>
    prev.includes(name) ? prev.filter(t => t !== name) : [...prev, name]
  )
}
```

- [ ] **Step 3: Update `clearFilters` to reset tags**

Replace the existing `clearFilters`:
```jsx
const clearFilters = () => {
  setSearchTerm('')
  setSelectedSource('')
  setSelectedLocation('')
  setShowPastEvents(false)
  setSelectedTags([])
}
```

- [ ] **Step 4: Update `filteredEvents` to include tag filter**

Replace the existing `filteredEvents` computation:
```jsx
const filteredEvents = allEvents.filter(event => {
  if (!showPastEvents && event.date && new Date(event.date) < now) return false
  if (searchTerm) {
    const s = searchTerm.toLowerCase()
    if (!event.title?.toLowerCase().includes(s) && !event.description?.toLowerCase().includes(s)) return false
  }
  if (selectedSource && event.source !== selectedSource) return false
  if (selectedLocation && event.location !== selectedLocation) return false
  if (selectedTags.length > 0) {
    const eventTags = event.tags || []
    if (!selectedTags.some(t => eventTags.includes(t))) return false
  }
  return true
}).sort((a, b) => {
  if (!a.date) return 1
  if (!b.date) return -1
  return new Date(a.date) - new Date(b.date)
})
```

- [ ] **Step 5: Update `hasFilters`**

Replace the existing `hasFilters`:
```jsx
const hasFilters = searchTerm || selectedSource || selectedLocation || showPastEvents || selectedTags.length > 0
```

- [ ] **Step 6: Add badge filter row to JSX**

Inside the `<div className="filters-section mb-4">` block, after the closing `</div>` of the existing `filter-row` div, add:
```jsx
          {/* Category tag filter */}
          <div className="filter-row" style={{ marginTop: '10px', gap: '8px', flexWrap: 'wrap', alignItems: 'center' }}>
            <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: 600, letterSpacing: '0.05em', flexShrink: 0 }}>
              KATEGORİ:
            </span>
            {Object.keys(TAG_STYLES).map(name => (
              <TagBadge
                key={name}
                name={name}
                selected={selectedTags.includes(name)}
                clickable
                onClick={() => toggleTag(name)}
              />
            ))}
          </div>
```

- [ ] **Step 7: Commit**

```bash
git add frontend/src/pages/HomePage.jsx
git commit -m "feat: add category tag filter badges to HomePage"
```

---

### Task 10: Frontend — EventCard tag badges

**Files:**
- Modify: `frontend/src/components/EventCard.jsx`

- [ ] **Step 1: Import TagBadge**

Add at the top of `EventCard.jsx`, after the existing imports:
```jsx
import TagBadge from './TagBadge'
```

- [ ] **Step 2: Render tags on the card**

Inside the `event-image-wrapper` div, after the closing `</span>` of `event-source-badge`, add:
```jsx
        {event.tags && event.tags.slice(0, 2).map(name => (
          <TagBadge key={name} name={name} />
        ))}
        {event.tags && event.tags.length > 2 && (
          <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)', fontWeight: 700 }}>
            +{event.tags.length - 2}
          </span>
        )}
```

The complete `event-image-wrapper` block becomes:
```jsx
      <div className="event-image-wrapper">
        <img
          src={event.image_url || '/placeholder-image-colored.webp'}
          alt={event.title}
          className="event-image"
          width="400"
          height="200"
          loading="lazy"
          onError={(e) => { e.target.src = '/placeholder-image-colored.webp' }}
        />
        <div className="event-image-overlay" />
        <span
          className="event-source-badge"
          style={{
            background: sourceStyle.bg,
            color: sourceStyle.color,
            border: `1px solid ${sourceStyle.border}`,
          }}
        >
          {event.source}
        </span>
        {event.tags && event.tags.slice(0, 2).map(name => (
          <TagBadge key={name} name={name} />
        ))}
        {event.tags && event.tags.length > 2 && (
          <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)', fontWeight: 700 }}>
            +{event.tags.length - 2}
          </span>
        )}
      </div>
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/EventCard.jsx
git commit -m "feat: show category tag badges on EventCard"
```

---

### Task 11: Run backfill and smoke test

- [ ] **Step 1: Run backfill on local DB (if running locally)**

```bash
python scripts/backfill_tags.py
```
Expected: `Backfilled N events.`

Or inside Docker:
```bash
docker-compose exec backend python scripts/backfill_tags.py
```

- [ ] **Step 2: Run full test suite**

```bash
pytest -v
```
Expected: all tests PASS, coverage ≥ 70%

- [ ] **Step 3: Start the app and verify visually**

```bash
docker-compose down && docker-compose up -d --build
```

Open `http://localhost:3000`. Verify:
- Category badge row appears below Platform/Location filters
- Clicking a badge filters the event list
- Event cards show category badge(s) alongside the source badge
- Clicking multiple badges (OR logic) works
- "Temizle" button resets tag selection
