# Test Coverage Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reach ≥70% coverage across `app/` and enforce it as a CI gate.

**Architecture:** Bottom-up — pure service unit tests first (SQLite in-memory via existing `test_db` fixture), then API integration tests (FastAPI `TestClient` with `get_db` overridden to SQLite), then HTML fixtures + tests for 3 remaining scrapers. Finally wire up `--cov-fail-under=70` in `pytest.ini`.

**Tech Stack:** pytest, pytest-cov, FastAPI TestClient, unittest.mock, BeautifulSoup

---

## File Map

| Action | Path | Purpose |
|---|---|---|
| Modify | `pytest.ini` | Add `addopts` with coverage flags and 70% gate |
| Modify | `tests/conftest.py` | Add `client` and `auth_headers` fixtures |
| Create | `tests/unit/test_date_extractor.py` | Unit tests for `extract_date_from_text` |
| Create | `tests/unit/test_event_service.py` | Unit tests for `EventService` |
| Create | `tests/unit/test_announcement_service.py` | Unit tests for `AnnouncementService` |
| Create | `tests/unit/test_suggestion_service.py` | Unit tests for `SuggestionService` |
| Create | `tests/unit/test_event_request_service.py` | Unit tests for `EventRequestService` |
| Create | `tests/unit/test_analytics_service.py` | Unit tests for `AnalyticsService` |
| Create | `tests/unit/test_auth_service.py` | Unit tests for `AuthService` |
| Create | `tests/unit/test_scraper_service.py` | Unit tests for `normalize_date` and `deactivate_past_events` |
| Create | `tests/integration/test_api_public.py` | TestClient tests for `/api/*` public routes |
| Create | `tests/integration/test_api_admin.py` | TestClient tests for `/api/admin/*` routes |
| Create | `tests/fixtures/akbank.html` | Minimal HTML fixture for akbank scraper |
| Create | `tests/fixtures/cs_scraper.html` | Minimal HTML fixture for cs_scraper |
| Create | `tests/fixtures/pupilica.html` | Minimal HTML fixture for pupilica scraper |
| Modify | `tests/unit/test_scrapers.py` | Add tests for akbank, cs_scraper, pupilica |

---

## Task 1: Update pytest.ini with coverage gate

**Files:**
- Modify: `pytest.ini`

- [ ] **Step 1: Replace pytest.ini content**

```ini
[pytest]
testpaths = tests
addopts = --cov=app --cov-report=xml --cov-fail-under=70
markers =
    integration: marks tests as integration tests (deselect with '-m "not integration"')
```

- [ ] **Step 2: Verify pytest still runs (coverage will be low — that's expected now)**

```bash
python -m pytest -m "not integration" -q --no-header 2>&1 | tail -5
```

Expected: Tests pass (coverage failure is acceptable until later tasks are complete — we'll fix the gate last).

- [ ] **Step 3: Commit**

```bash
git add pytest.ini
git commit -m "test: add coverage gate (--cov-fail-under=70) to pytest.ini"
```

---

## Task 2: Add `client` and `auth_headers` fixtures to conftest.py

**Files:**
- Modify: `tests/conftest.py`

- [ ] **Step 1: Add fixtures after the existing `invalid_event` fixture**

Open `tests/conftest.py` and append the following at the end of the file:

```python
from fastapi.testclient import TestClient


@pytest.fixture
def client(test_db):
    from app.main import app
    from app.core.database import get_db

    app.dependency_overrides[get_db] = lambda: test_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client):
    import os

    resp = client.post(
        "/api/admin/login",
        json={
            "username": os.environ["ADMIN_USERNAME"],
            "password": os.environ["ADMIN_PASSWORD"],
        },
    )
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
```

- [ ] **Step 2: Run a quick smoke check to confirm the fixtures import cleanly**

```bash
python -m pytest tests/unit/test_validators.py -q --no-header 2>&1 | tail -3
```

Expected: All existing validator tests pass.

- [ ] **Step 3: Commit**

```bash
git add tests/conftest.py
git commit -m "test: add TestClient and auth_headers fixtures to conftest"
```

---

## Task 3: Unit tests for `date_extractor`

**Files:**
- Create: `tests/unit/test_date_extractor.py`

- [ ] **Step 1: Create the test file**

```python
import os

os.environ.setdefault("ALLOW_INSECURE_DEFAULTS", "true")
os.environ.setdefault("SECRET_KEY", "test-secret-key-that-is-at-least-32-chars")
os.environ.setdefault("ADMIN_USERNAME", "testadmin")
os.environ.setdefault("ADMIN_PASSWORD", "testpassword")

from datetime import datetime
from app.services.date_extractor import extract_date_from_text


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
```

- [ ] **Step 2: Run tests**

```bash
python -m pytest tests/unit/test_date_extractor.py -v --no-cov 2>&1 | tail -10
```

Expected: All 5 tests pass.

- [ ] **Step 3: Commit**

```bash
git add tests/unit/test_date_extractor.py
git commit -m "test: add unit tests for date_extractor"
```

---

## Task 4: Unit tests for `EventService`

**Files:**
- Create: `tests/unit/test_event_service.py`

- [ ] **Step 1: Create the test file**

```python
import os

os.environ.setdefault("ALLOW_INSECURE_DEFAULTS", "true")
os.environ.setdefault("SECRET_KEY", "test-secret-key-that-is-at-least-32-chars")
os.environ.setdefault("ADMIN_USERNAME", "testadmin")
os.environ.setdefault("ADMIN_PASSWORD", "testpassword")

import pytest
from app.services.event_service import EventService
from app.schemas.event import EventCreate, EventUpdate


def _create_data(**kwargs) -> EventCreate:
    defaults = dict(
        title="Python Bootcamp Istanbul",
        description="A great bootcamp",
        url="https://example.com/event",
        source="test",
        is_active=True,
    )
    defaults.update(kwargs)
    return EventCreate(**defaults)


def test_create_and_get_event(test_db):
    service = EventService(test_db)
    event = service.create_event(_create_data())
    assert event.id is not None
    assert event.title == "Python Bootcamp Istanbul"
    assert event.source == "test"


def test_get_event_by_id(test_db):
    service = EventService(test_db)
    created = service.create_event(_create_data())
    fetched = service.get_event_by_id(created.id)
    assert fetched is not None
    assert fetched.id == created.id


def test_get_event_by_id_not_found(test_db):
    service = EventService(test_db)
    assert service.get_event_by_id(9999) is None


def test_get_events_active_only(test_db):
    service = EventService(test_db)
    service.create_event(_create_data(url="https://example.com/a", is_active=True))
    service.create_event(_create_data(url="https://example.com/b", is_active=False))
    active = service.get_events(active_only=True)
    assert len(active) == 1
    assert all(e.is_active for e in active)


def test_get_events_all(test_db):
    service = EventService(test_db)
    service.create_event(_create_data(url="https://example.com/a", is_active=True))
    service.create_event(_create_data(url="https://example.com/b", is_active=False))
    all_events = service.get_events(active_only=False)
    assert len(all_events) == 2


def test_update_event_title(test_db):
    service = EventService(test_db)
    created = service.create_event(_create_data())
    updated = service.update_event(created.id, EventUpdate(title="New Title"))
    assert updated is not None
    assert updated.title == "New Title"


def test_update_event_not_found_returns_none(test_db):
    service = EventService(test_db)
    result = service.update_event(9999, EventUpdate(title="X"))
    assert result is None


def test_delete_event(test_db):
    service = EventService(test_db)
    created = service.create_event(_create_data())
    assert service.delete_event(created.id) is True
    assert service.get_event_by_id(created.id) is None


def test_delete_event_not_found(test_db):
    service = EventService(test_db)
    assert service.delete_event(9999) is False


def test_duplicate_url_raises(test_db):
    service = EventService(test_db)
    service.create_event(_create_data())
    with pytest.raises(ValueError, match="already exists"):
        service.create_event(_create_data())


def test_get_total_active_events(test_db):
    service = EventService(test_db)
    service.create_event(_create_data(url="https://example.com/a", is_active=True))
    service.create_event(_create_data(url="https://example.com/b", is_active=False))
    assert service.get_total_active_events() == 1


def test_get_last_updated_event(test_db):
    service = EventService(test_db)
    service.create_event(_create_data())
    latest = service.get_last_updated_event()
    assert latest is not None
```

- [ ] **Step 2: Run tests**

```bash
python -m pytest tests/unit/test_event_service.py -v --no-cov 2>&1 | tail -15
```

Expected: All 12 tests pass.

- [ ] **Step 3: Commit**

```bash
git add tests/unit/test_event_service.py
git commit -m "test: add unit tests for EventService"
```

---

## Task 5: Unit tests for `AnnouncementService`, `SuggestionService`, `EventRequestService`

**Files:**
- Create: `tests/unit/test_announcement_service.py`
- Create: `tests/unit/test_suggestion_service.py`
- Create: `tests/unit/test_event_request_service.py`

- [ ] **Step 1: Create `tests/unit/test_announcement_service.py`**

```python
import os

os.environ.setdefault("ALLOW_INSECURE_DEFAULTS", "true")
os.environ.setdefault("SECRET_KEY", "test-secret-key-that-is-at-least-32-chars")
os.environ.setdefault("ADMIN_USERNAME", "testadmin")
os.environ.setdefault("ADMIN_PASSWORD", "testpassword")

import pytest
from app.services.announcement_service import AnnouncementService
from app.schemas.announcement import AnnouncementCreate


def test_create_and_get_announcement(test_db):
    service = AnnouncementService(test_db)
    created = service.create_announcement(
        AnnouncementCreate(title="Hello", message="World")
    )
    assert created.id is not None
    assert created.title == "Hello"
    assert created.message == "World"


def test_get_announcements_returns_list(test_db):
    service = AnnouncementService(test_db)
    service.create_announcement(AnnouncementCreate(title="A", message="msg"))
    service.create_announcement(AnnouncementCreate(title="B", message="msg"))
    items = service.get_announcements()
    assert len(items) == 2


def test_get_announcement_by_id(test_db):
    service = AnnouncementService(test_db)
    created = service.create_announcement(AnnouncementCreate(title="X", message="Y"))
    fetched = service.get_announcement_by_id(created.id)
    assert fetched is not None
    assert fetched.id == created.id


def test_get_announcement_by_id_not_found(test_db):
    service = AnnouncementService(test_db)
    assert service.get_announcement_by_id(9999) is None


def test_get_latest_announcement(test_db):
    service = AnnouncementService(test_db)
    service.create_announcement(AnnouncementCreate(title="First", message="m"))
    service.create_announcement(AnnouncementCreate(title="Second", message="m"))
    latest = service.get_latest_announcement()
    assert latest is not None


def test_delete_announcement(test_db):
    service = AnnouncementService(test_db)
    created = service.create_announcement(AnnouncementCreate(title="Del", message="m"))
    assert service.delete_announcement(created.id) is True
    assert service.get_announcement_by_id(created.id) is None


def test_delete_announcement_not_found(test_db):
    service = AnnouncementService(test_db)
    assert service.delete_announcement(9999) is False
```

- [ ] **Step 2: Create `tests/unit/test_suggestion_service.py`**

```python
import os

os.environ.setdefault("ALLOW_INSECURE_DEFAULTS", "true")
os.environ.setdefault("SECRET_KEY", "test-secret-key-that-is-at-least-32-chars")
os.environ.setdefault("ADMIN_USERNAME", "testadmin")
os.environ.setdefault("ADMIN_PASSWORD", "testpassword")

import pytest
from app.services.suggestion_service import SuggestionService
from app.schemas.suggestion import SuggestionCreate


def _sug(**kwargs) -> SuggestionCreate:
    defaults = dict(
        suggestion_type="oneri",
        suggestion_title="Better search",
        suggestion_text="Add full-text search please",
    )
    defaults.update(kwargs)
    return SuggestionCreate(**defaults)


def test_create_and_get_suggestion(test_db):
    service = SuggestionService(test_db)
    created = service.create_suggestion(_sug())
    assert created.id is not None
    assert created.suggestion_title == "Better search"


def test_get_suggestions_returns_list(test_db):
    service = SuggestionService(test_db)
    service.create_suggestion(_sug(suggestion_title="A"))
    service.create_suggestion(_sug(suggestion_title="B"))
    items = service.get_suggestions()
    assert len(items) == 2


def test_get_suggestion_by_id(test_db):
    service = SuggestionService(test_db)
    created = service.create_suggestion(_sug())
    fetched = service.get_suggestion_by_id(created.id)
    assert fetched is not None
    assert fetched.id == created.id


def test_get_suggestion_by_id_not_found(test_db):
    service = SuggestionService(test_db)
    assert service.get_suggestion_by_id(9999) is None


def test_delete_suggestion(test_db):
    service = SuggestionService(test_db)
    created = service.create_suggestion(_sug())
    assert service.delete_suggestion(created.id) is True
    assert service.get_suggestion_by_id(created.id) is None


def test_delete_suggestion_not_found(test_db):
    service = SuggestionService(test_db)
    assert service.delete_suggestion(9999) is False
```

- [ ] **Step 3: Create `tests/unit/test_event_request_service.py`**

```python
import os

os.environ.setdefault("ALLOW_INSECURE_DEFAULTS", "true")
os.environ.setdefault("SECRET_KEY", "test-secret-key-that-is-at-least-32-chars")
os.environ.setdefault("ADMIN_USERNAME", "testadmin")
os.environ.setdefault("ADMIN_PASSWORD", "testpassword")

import pytest
from app.services.event_request_service import EventRequestService
from app.schemas.event_request import EventRequestCreate


def _req(**kwargs) -> EventRequestCreate:
    defaults = dict(
        event_link="https://example.com/event",
        event_title="Cool Hackathon",
    )
    defaults.update(kwargs)
    return EventRequestCreate(**defaults)


def test_create_and_get_event_request(test_db):
    service = EventRequestService(test_db)
    created = service.create_event_request(_req())
    assert created.id is not None
    assert created.event_title == "Cool Hackathon"


def test_get_event_requests_returns_list(test_db):
    service = EventRequestService(test_db)
    service.create_event_request(_req(event_link="https://example.com/a"))
    service.create_event_request(_req(event_link="https://example.com/b"))
    items = service.get_event_requests()
    assert len(items) == 2


def test_get_event_request_by_id(test_db):
    service = EventRequestService(test_db)
    created = service.create_event_request(_req())
    fetched = service.get_event_request_by_id(created.id)
    assert fetched is not None
    assert fetched.id == created.id


def test_get_event_request_by_id_not_found(test_db):
    service = EventRequestService(test_db)
    assert service.get_event_request_by_id(9999) is None


def test_delete_event_request(test_db):
    service = EventRequestService(test_db)
    created = service.create_event_request(_req())
    assert service.delete_event_request(created.id) is True
    assert service.get_event_request_by_id(created.id) is None


def test_delete_event_request_not_found(test_db):
    service = EventRequestService(test_db)
    assert service.delete_event_request(9999) is False
```

- [ ] **Step 4: Run all three new test files**

```bash
python -m pytest tests/unit/test_announcement_service.py tests/unit/test_suggestion_service.py tests/unit/test_event_request_service.py -v --no-cov 2>&1 | tail -20
```

Expected: All 19 tests pass.

- [ ] **Step 5: Commit**

```bash
git add tests/unit/test_announcement_service.py tests/unit/test_suggestion_service.py tests/unit/test_event_request_service.py
git commit -m "test: add unit tests for Announcement, Suggestion, EventRequest services"
```

---

## Task 6: Unit tests for `AnalyticsService` and `AuthService`

**Files:**
- Create: `tests/unit/test_analytics_service.py`
- Create: `tests/unit/test_auth_service.py`

- [ ] **Step 1: Create `tests/unit/test_analytics_service.py`**

```python
import os

os.environ.setdefault("ALLOW_INSECURE_DEFAULTS", "true")
os.environ.setdefault("SECRET_KEY", "test-secret-key-that-is-at-least-32-chars")
os.environ.setdefault("ADMIN_USERNAME", "testadmin")
os.environ.setdefault("ADMIN_PASSWORD", "testpassword")

from app.services.analytics_service import AnalyticsService


def test_get_stats_empty_db_returns_expected_shape(test_db):
    service = AnalyticsService(test_db)
    stats = service.get_stats()
    assert "daily_traffic" in stats
    assert "today_visitors" in stats
    assert "total_visitors" in stats
    assert "top_pages" in stats
    assert isinstance(stats["daily_traffic"], list)
    assert isinstance(stats["top_pages"], list)
    assert stats["today_visitors"] == 0
    assert stats["total_visitors"] == 0


def test_log_request_increments_total(test_db):
    service = AnalyticsService(test_db)
    service.log_request("/api/events", "GET", "127.0.0.1", "pytest-agent")
    service.log_request("/api/events", "GET", "127.0.0.1", "pytest-agent")
    stats = service.get_stats()
    assert stats["total_visitors"] == 2


def test_top_pages_sorted_by_count(test_db):
    service = AnalyticsService(test_db)
    for _ in range(3):
        service.log_request("/api/events", "GET", "1.1.1.1", "ua")
    service.log_request("/api/announcements", "GET", "1.1.1.1", "ua")
    stats = service.get_stats()
    paths = [p["path"] for p in stats["top_pages"]]
    assert paths[0] == "/api/events"
```

- [ ] **Step 2: Create `tests/unit/test_auth_service.py`**

```python
import os

os.environ.setdefault("ALLOW_INSECURE_DEFAULTS", "true")
os.environ.setdefault("SECRET_KEY", "test-secret-key-that-is-at-least-32-chars")
os.environ.setdefault("ADMIN_USERNAME", "testadmin")
os.environ.setdefault("ADMIN_PASSWORD", "testpassword")

from app.services.auth_service import AuthService


def test_authenticate_valid_credentials():
    service = AuthService()
    assert service.authenticate_user("testadmin", "testpassword") is True


def test_authenticate_wrong_password():
    service = AuthService()
    assert service.authenticate_user("testadmin", "wrongpass") is False


def test_authenticate_wrong_username():
    service = AuthService()
    assert service.authenticate_user("hacker", "testpassword") is False


def test_create_and_verify_token():
    service = AuthService()
    token = service.create_access_token({"sub": "testadmin"})
    username = service.verify_token(token)
    assert username == "testadmin"


def test_verify_invalid_token_returns_none():
    service = AuthService()
    assert service.verify_token("not.a.token") is None


def test_hash_and_verify_password():
    service = AuthService()
    hashed = service.get_password_hash("mysecret")
    assert service.verify_password("mysecret", hashed) is True
    assert service.verify_password("wrong", hashed) is False
```

- [ ] **Step 3: Run both new test files**

```bash
python -m pytest tests/unit/test_analytics_service.py tests/unit/test_auth_service.py -v --no-cov 2>&1 | tail -15
```

Expected: All 9 tests pass.

- [ ] **Step 4: Commit**

```bash
git add tests/unit/test_analytics_service.py tests/unit/test_auth_service.py
git commit -m "test: add unit tests for AnalyticsService and AuthService"
```

---

## Task 7: Unit tests for `scraper_service` module-level functions

**Files:**
- Create: `tests/unit/test_scraper_service.py`

The `normalize_date` and `deactivate_past_events` functions are module-level (not inside `ScraperService`). `deactivate_past_events` internally calls `SessionLocal()` — we patch that to inject our test DB.

- [ ] **Step 1: Create the test file**

```python
import os

os.environ.setdefault("ALLOW_INSECURE_DEFAULTS", "true")
os.environ.setdefault("SECRET_KEY", "test-secret-key-that-is-at-least-32-chars")
os.environ.setdefault("ADMIN_USERNAME", "testadmin")
os.environ.setdefault("ADMIN_PASSWORD", "testpassword")

from datetime import datetime, timedelta
from unittest.mock import patch
import pytest
from app.services.scraper_service import normalize_date, deactivate_past_events
from app.models.event import Event


# ── normalize_date ────────────────────────────────────────────────────────────


def test_normalize_date_none():
    assert normalize_date(None) is None


def test_normalize_date_empty_string():
    assert normalize_date("") is None


def test_normalize_date_datetime_passthrough():
    dt = datetime(2027, 5, 15)
    assert normalize_date(dt) == dt


def test_normalize_date_invalid_text():
    assert normalize_date("tarih belirtilmemiş") is None
    assert normalize_date("-") is None


def test_normalize_date_valid_turkish_string():
    result = normalize_date("15 Mayıs 2027")
    assert isinstance(result, datetime)
    assert result.month == 5


# ── deactivate_past_events ────────────────────────────────────────────────────


def test_deactivate_past_events(test_db):
    past = Event(
        title="Past Event",
        url="https://example.com/past",
        source="test",
        is_active=True,
        date=datetime.now() - timedelta(days=2),
        scraped_at=datetime.now(),
    )
    future = Event(
        title="Future Event",
        url="https://example.com/future",
        source="test",
        is_active=True,
        date=datetime.now() + timedelta(days=2),
        scraped_at=datetime.now(),
    )
    test_db.add_all([past, future])
    test_db.commit()

    with patch(
        "app.services.scraper_service.SessionLocal", return_value=test_db
    ):
        count = deactivate_past_events()

    assert count == 1
    test_db.refresh(past)
    test_db.refresh(future)
    assert past.is_active is False
    assert future.is_active is True
```

- [ ] **Step 2: Run the tests**

```bash
python -m pytest tests/unit/test_scraper_service.py -v --no-cov 2>&1 | tail -15
```

Expected: All 7 tests pass. The `deactivate_past_events` patch works because the function calls `SessionLocal()` at the start — we replace `SessionLocal` with a callable that returns our `test_db` directly, so it uses our in-memory DB. Note: the function calls `db.close()` in a `finally` block; SQLite in-memory sessions handle this gracefully.

- [ ] **Step 3: Commit**

```bash
git add tests/unit/test_scraper_service.py
git commit -m "test: add unit tests for scraper_service module functions"
```

---

## Task 8: API tests — public routes

**Files:**
- Create: `tests/integration/test_api_public.py`

These tests use the `client` fixture from conftest (FastAPI TestClient with SQLite). They live in `tests/integration/` for organisation but carry **no** `integration` marker, so CI runs them in the standard job.

- [ ] **Step 1: Create the test file**

```python
import os

os.environ.setdefault("ALLOW_INSECURE_DEFAULTS", "true")
os.environ.setdefault("SECRET_KEY", "test-secret-key-that-is-at-least-32-chars")
os.environ.setdefault("ADMIN_USERNAME", "testadmin")
os.environ.setdefault("ADMIN_PASSWORD", "testpassword")

import pytest
from app.models.event import Event
from app.models.announcement import Announcement
from datetime import datetime


def _seed_event(db, url="https://example.com/ev", is_active=True):
    e = Event(
        title="Test Event",
        url=url,
        source="test",
        is_active=is_active,
        scraped_at=datetime.now(),
    )
    db.add(e)
    db.commit()
    db.refresh(e)
    return e


def _seed_announcement(db, title="Notice", message="Hello"):
    a = Announcement(title=title, message=message)
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


# ── /health ───────────────────────────────────────────────────────────────────


def test_health_check(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


# ── /api/events ───────────────────────────────────────────────────────────────


def test_get_events_empty(client):
    resp = client.get("/api/events")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_count"] == 0
    assert data["events"] == []


def test_get_events_returns_active_events(client, test_db):
    _seed_event(test_db, url="https://example.com/a", is_active=True)
    _seed_event(test_db, url="https://example.com/b", is_active=False)
    resp = client.get("/api/events?active_only=true")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_count"] == 1
    assert len(data["events"]) == 1


def test_get_events_all_when_active_only_false(client, test_db):
    _seed_event(test_db, url="https://example.com/a", is_active=True)
    _seed_event(test_db, url="https://example.com/b", is_active=False)
    resp = client.get("/api/events?active_only=false")
    assert resp.status_code == 200
    assert len(resp.json()["events"]) == 2


# ── /api/announcements ────────────────────────────────────────────────────────


def test_get_announcements_empty(client):
    resp = client.get("/api/announcements")
    assert resp.status_code == 200
    assert resp.json()["total_count"] == 0


def test_get_announcements_returns_items(client, test_db):
    _seed_announcement(test_db, title="First")
    _seed_announcement(test_db, title="Second")
    resp = client.get("/api/announcements")
    assert resp.status_code == 200
    assert resp.json()["total_count"] == 2


def test_get_latest_announcement_none(client):
    resp = client.get("/api/announcements/latest")
    assert resp.status_code == 200
    assert resp.json() is None


def test_get_latest_announcement_returns_item(client, test_db):
    _seed_announcement(test_db, title="Latest")
    resp = client.get("/api/announcements/latest")
    assert resp.status_code == 200
    assert resp.json()["title"] == "Latest"


# ── /api/suggestions ─────────────────────────────────────────────────────────


def test_post_suggestion(client):
    payload = {
        "suggestion_type": "oneri",
        "suggestion_title": "Better UI",
        "suggestion_text": "Please improve the mobile UI",
    }
    resp = client.post("/api/suggestions", json=payload)
    assert resp.status_code == 200
    assert resp.json()["suggestion_title"] == "Better UI"


# ── /api/event-requests ───────────────────────────────────────────────────────


def test_post_event_request(client):
    payload = {
        "event_link": "https://example.com/hackathon",
        "event_title": "Global Hackathon",
    }
    resp = client.post("/api/event-requests", json=payload)
    assert resp.status_code == 200
    assert resp.json()["event_title"] == "Global Hackathon"
```

- [ ] **Step 2: Run the tests**

```bash
python -m pytest tests/integration/test_api_public.py -v --no-cov 2>&1 | tail -20
```

Expected: All 11 tests pass.

- [ ] **Step 3: Commit**

```bash
git add tests/integration/test_api_public.py
git commit -m "test: add API tests for public routes"
```

---

## Task 9: API tests — admin routes

**Files:**
- Create: `tests/integration/test_api_admin.py`

- [ ] **Step 1: Create the test file**

```python
import os

os.environ.setdefault("ALLOW_INSECURE_DEFAULTS", "true")
os.environ.setdefault("SECRET_KEY", "test-secret-key-that-is-at-least-32-chars")
os.environ.setdefault("ADMIN_USERNAME", "testadmin")
os.environ.setdefault("ADMIN_PASSWORD", "testpassword")

import pytest
from app.models.event import Event
from app.models.announcement import Announcement
from datetime import datetime


def _seed_event(db, url="https://example.com/ev"):
    e = Event(
        title="Admin Event",
        url=url,
        source="test",
        is_active=True,
        scraped_at=datetime.now(),
    )
    db.add(e)
    db.commit()
    db.refresh(e)
    return e


# ── auth ──────────────────────────────────────────────────────────────────────


def test_login_success(client):
    resp = client.post(
        "/api/admin/login",
        json={"username": "testadmin", "password": "testpassword"},
    )
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_wrong_password(client):
    resp = client.post(
        "/api/admin/login",
        json={"username": "testadmin", "password": "wrong"},
    )
    assert resp.status_code == 401


# ── protected endpoints require auth ─────────────────────────────────────────


def test_get_admin_events_requires_auth(client):
    resp = client.get("/api/admin/events")
    assert resp.status_code == 403


def test_create_event_requires_auth(client):
    resp = client.post("/api/admin/events", json={})
    assert resp.status_code == 403


# ── event CRUD ────────────────────────────────────────────────────────────────


def test_get_admin_events_with_auth(client, auth_headers):
    resp = client.get("/api/admin/events", headers=auth_headers)
    assert resp.status_code == 200
    assert "events" in resp.json()


def test_create_event_with_auth(client, auth_headers):
    payload = {
        "title": "New Admin Event",
        "url": "https://example.com/new",
        "source": "admin",
        "is_active": True,
    }
    resp = client.post("/api/admin/events", json=payload, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["title"] == "New Admin Event"


def test_update_event_with_auth(client, auth_headers, test_db):
    event = _seed_event(test_db)
    resp = client.put(
        f"/api/admin/events/{event.id}",
        json={"title": "Updated Title"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "Updated Title"


def test_delete_event_with_auth(client, auth_headers, test_db):
    event = _seed_event(test_db)
    resp = client.delete(f"/api/admin/events/{event.id}", headers=auth_headers)
    assert resp.status_code == 200


def test_delete_event_not_found(client, auth_headers):
    resp = client.delete("/api/admin/events/99999", headers=auth_headers)
    assert resp.status_code == 404


# ── announcements ─────────────────────────────────────────────────────────────


def test_create_announcement_with_auth(client, auth_headers):
    payload = {"title": "System Notice", "message": "Maintenance tonight."}
    resp = client.post("/api/admin/announcements", json=payload, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["title"] == "System Notice"


def test_delete_announcement_with_auth(client, auth_headers, test_db):
    a = Announcement(title="To Delete", message="bye")
    test_db.add(a)
    test_db.commit()
    test_db.refresh(a)
    resp = client.delete(f"/api/admin/announcements/{a.id}", headers=auth_headers)
    assert resp.status_code == 200
```

- [ ] **Step 2: Run the tests**

```bash
python -m pytest tests/integration/test_api_admin.py -v --no-cov 2>&1 | tail -20
```

Expected: All 11 tests pass. If any fail, check that the admin route paths match exactly. Look at `app/api/admin.py` to verify — the router is mounted at `/api/admin` per `app/api/__init__.py`.

- [ ] **Step 3: Commit**

```bash
git add tests/integration/test_api_admin.py
git commit -m "test: add API tests for admin routes"
```

---

## Task 10: HTML fixtures for akbank, cs_scraper, pupilica

**Files:**
- Create: `tests/fixtures/akbank.html`
- Create: `tests/fixtures/cs_scraper.html`
- Create: `tests/fixtures/pupilica.html`

The fixtures must match the CSS selectors used by each scraper's parsing logic.

- [ ] **Step 1: Create `tests/fixtures/akbank.html`**

The akbank scraper looks for `div.event-item`, inside which it finds `h6.text-primary > a[href]` for the link, `img[src]` for the image, and `card.get("data-startdate")` for the date.

```html
<!DOCTYPE html>
<html>
<body>
<div id="event-list-all">
  <div class="event-item" data-startdate="2027-06-15T10:00:00Z">
    <h6 class="text-primary">
      <a href="/etkinlik/python-bootcamp">Python Bootcamp</a>
    </h6>
    <a class="img-link" href="/etkinlik/python-bootcamp">
      <img src="https://akbankgenclikakademisi.com/img/event.jpg" alt="event">
    </a>
    <div class="info-list">
      <div class="d-flex">
        <span>Etkinlik Yeri</span><span>:</span><span>Online</span>
      </div>
    </div>
  </div>
</div>
</body>
</html>
```

- [ ] **Step 2: Create `tests/fixtures/cs_scraper.html`**

The cs_scraper looks for `div.event-card, div.card, article` with an `h3/h2/h4` title element and `a[href]` link.

```html
<!DOCTYPE html>
<html>
<body>
  <div class="event-card">
    <h3>Coderspace Hackathon</h3>
    <a href="/etkinlikler/hackathon-2027">Etkinliğe Git</a>
    <span class="event-date">20 Haziran 2027</span>
    <p class="event-description">Hackathon açıklaması burada.</p>
    <img src="https://coderspace.io/img/hack.jpg" alt="event">
  </div>
  <div class="event-card">
    <h3>Web Dev Workshop</h3>
    <a href="https://coderspace.io/etkinlikler/webdev">Workshop Linki</a>
    <span class="event-date">25 Haziran 2027</span>
    <p class="event-description">Workshop açıklaması.</p>
  </div>
</body>
</html>
```

- [ ] **Step 3: Create `tests/fixtures/pupilica.html`**

The pupilica scraper looks for `div[class*='EventsCard__CardWrapper']` with `h3` for the title and `a[href]` for the link.

```html
<!DOCTYPE html>
<html>
<body>
  <div class="EventsCard__CardWrapper-sc-123">
    <h3>Data Science Bootcamp</h3>
    <img src="https://pupilica.com/img/ds.jpg" alt="event">
    <span>Tarih</span><span>15 Temmuz 2027</span>
    <span>Son Başvuru</span><span>10 Temmuz 2027</span>
    <a href="/events/data-science-bootcamp">Detaylar</a>
  </div>
  <div class="EventsCard__CardWrapper-sc-456">
    <h3>Frontend Masterclass</h3>
    <a href="/events/frontend-masterclass">Detaylar</a>
  </div>
</body>
</html>
```

- [ ] **Step 4: Commit the fixtures**

```bash
git add tests/fixtures/akbank.html tests/fixtures/cs_scraper.html tests/fixtures/pupilica.html
git commit -m "test: add HTML fixtures for akbank, cs_scraper, pupilica scrapers"
```

---

## Task 11: Scraper tests for akbank, cs_scraper, pupilica

**Files:**
- Modify: `tests/unit/test_scrapers.py`

Append the following three test sections to the existing `tests/unit/test_scrapers.py`. Do not remove any existing tests.

- [ ] **Step 1: Open `tests/unit/test_scrapers.py` and append akbank tests**

Add at the end of the file:

```python
# ── Akbank ────────────────────────────────────────────────────────────────────


def test_akbank_returns_events():
    from app.scrapers.akbank_scraper import scrape_akbank_events

    mock_driver = _make_selenium_driver(_html("akbank.html"))

    with patch(
        "app.scrapers.akbank_scraper.uc.Chrome", return_value=mock_driver
    ), patch(
        "app.scrapers.akbank_scraper.WebDriverWait"
    ), patch(
        "app.scrapers.akbank_scraper.get_chrome_options"
    ):
        events = scrape_akbank_events()

    assert isinstance(events, list)
    assert len(events) >= 1
    assert all("title" in e for e in events)
    assert all("url" in e for e in events)


# ── CS Scraper (Coderspace) ───────────────────────────────────────────────────


def test_cs_scraper_returns_events():
    from app.scrapers.cs_scraper import scrape_coderspace_events

    mock_driver = _make_selenium_driver(_html("cs_scraper.html"))
    mock_driver.find_elements.return_value = []  # no Cloudflare challenge

    with patch(
        "app.scrapers.cs_scraper.uc.Chrome", return_value=mock_driver
    ), patch(
        "app.scrapers.cs_scraper.WebDriverWait"
    ), patch(
        "app.scrapers.cs_scraper.time.sleep"
    ):
        events = scrape_coderspace_events()

    assert isinstance(events, list)
    assert len(events) >= 1
    assert all("title" in e for e in events)
    assert all("url" in e for e in events)


# ── Pupilica ──────────────────────────────────────────────────────────────────


def test_pupilica_returns_events():
    from app.scrapers.pupilica_scraper import scrape_pupilica_events

    mock_driver = _make_selenium_driver(_html("pupilica.html"))

    with patch(
        "app.scrapers.pupilica_scraper.uc.Chrome", return_value=mock_driver
    ), patch(
        "app.scrapers.pupilica_scraper.WebDriverWait"
    ), patch(
        "app.scrapers.pupilica_scraper.get_chrome_options"
    ):
        events = scrape_pupilica_events()

    assert isinstance(events, list)
    assert len(events) >= 1
    assert all("title" in e for e in events)
    assert all("url" in e for e in events)
```

- [ ] **Step 2: Run all scraper tests**

```bash
python -m pytest tests/unit/test_scrapers.py -v --no-cov 2>&1 | tail -20
```

Expected: All existing tests still pass, plus 3 new ones. If any new test fails, the most likely cause is that the mock driver needs additional attributes — check the error message. Common fix: `mock_driver.find_elements = MagicMock(return_value=[])`.

- [ ] **Step 3: Commit**

```bash
git add tests/unit/test_scrapers.py
git commit -m "test: add scraper tests for akbank, cs_scraper, and pupilica"
```

---

## Task 12: Verify coverage gate passes

- [ ] **Step 1: Run the full non-integration test suite with coverage**

```bash
python -m pytest -m "not integration" -q 2>&1 | tail -10
```

Expected: All tests pass AND the coverage report shows ≥70%. The `--cov-fail-under=70` in `pytest.ini` will cause a non-zero exit if coverage is below 70%.

If coverage is below 70%, check which modules are least covered:

```bash
python -m pytest -m "not integration" -q --cov-report=term-missing 2>&1 | grep -E "TOTAL|[0-9]+%"
```

Identify any large uncovered module and add targeted tests. The most likely gap is `app/api/admin.py` — add more tests to `test_api_admin.py` covering the subscriber and event request admin routes.

- [ ] **Step 2: Commit final state**

```bash
git add -A
git commit -m "test: all tests passing with ≥70% coverage gate"
```

---

## Self-Review Against Spec

| Spec requirement | Task that covers it |
|---|---|
| `test_date_extractor.py` | Task 3 |
| `test_event_service.py` | Task 4 |
| `test_announcement_service.py`, `test_suggestion_service.py`, `test_event_request_service.py` | Task 5 |
| `test_analytics_service.py`, `test_auth_service.py` | Task 6 |
| `test_scraper_service.py` (normalize_date, deactivate_past_events) | Task 7 |
| `tests/integration/test_api_public.py` | Task 8 |
| `tests/integration/test_api_admin.py` | Task 9 |
| HTML fixtures: akbank, cs_scraper, pupilica | Task 10 |
| Scraper tests: akbank, cs_scraper, pupilica | Task 11 |
| `pytest.ini` coverage gate `--cov-fail-under=70` | Task 1 |
| `conftest.py` `client` + `auth_headers` fixtures | Task 2 |
| ≥70% gate verified in CI | Task 12 |

All spec requirements are covered. No TBDs found. Method names are consistent across all tasks.
