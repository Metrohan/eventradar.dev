# Test Coverage Design — EventRadar.dev
**Date:** 2026-05-08  
**Goal:** Reach ≥70% coverage across `app/` and enforce it as a CI gate.  
**Approach:** Bottom-up — service unit tests → API integration tests → missing scraper fixtures.

---

## Current State

| Area | Status |
|---|---|
| `test_validators.py` | ✅ complete |
| `test_scrapers.py` | ✅ youthall, techcareer, kodluyoruz, anbean |
| `test_services.py` | ✅ notification service only |
| All other services | ❌ no tests |
| API endpoints | ❌ no tests |
| akbank / cs_scraper / pupilica scrapers | ❌ no HTML fixtures |

CI already runs `pytest -m "not integration" --cov=app --cov-report=xml` but no `--fail-under` gate exists yet.

---

## Target File List

### Layer 1 — Service unit tests (new files)

| File | Modules under test |
|---|---|
| `tests/unit/test_date_extractor.py` | `app.services.date_extractor.extract_date_from_text` |
| `tests/unit/test_event_service.py` | `app.services.event_service.EventService` |
| `tests/unit/test_announcement_service.py` | `app.services.announcement_service.AnnouncementService` |
| `tests/unit/test_suggestion_service.py` | `app.services.suggestion_service.SuggestionService` |
| `tests/unit/test_event_request_service.py` | `app.services.event_request_service.EventRequestService` |
| `tests/unit/test_analytics_service.py` | `app.services.analytics_service.AnalyticsService` |
| `tests/unit/test_auth_service.py` | `app.services.auth_service.AuthService` |
| `tests/unit/test_scraper_service.py` | `app.services.scraper_service` (normalize_date, deactivate_past_events, process_scraped_events) |

### Layer 2 — API tests (new files, same CI job as unit tests)

| File | Routes covered |
|---|---|
| `tests/integration/test_api_public.py` | `GET /api/events`, `GET /api/announcements`, `GET /health` |
| `tests/integration/test_api_admin.py` | Admin CRUD for events, announcements, subscribers; auth 401/200 |

These use `FastAPI TestClient` with `get_db` overridden to the in-memory SQLite session. They are **not** marked `integration` (no external services needed) so they run in the same CI job.

### Layer 3 — Missing scraper fixtures + tests

| Fixture file | Scraper |
|---|---|
| `tests/fixtures/akbank.html` | `app.scrapers.akbank_scraper` |
| `tests/fixtures/cs_scraper.html` | `app.scrapers.cs_scraper` |
| `tests/fixtures/pupilica.html` | `app.scrapers.pupilica_scraper` |

Tests added to `tests/unit/test_scrapers.py` following the same pattern as youthall/techcareer:
- Happy path: mock Selenium/requests, feed fixture HTML, assert `len(events) >= 1` and required keys present
- No-chromedriver path: mock returns `None`, assert `events == []`

---

## Infrastructure Changes

### `pytest.ini`
Add to `addopts`:
```ini
--cov=app --cov-report=xml --cov-fail-under=70
```
This enforces the gate locally and in CI without any workflow file changes (CI already passes `pytest` addopts through).

### `tests/conftest.py` additions

**`client` fixture** — overrides `get_db` with the in-memory SQLite session:
```python
@pytest.fixture
def client(test_db):
    from app.main import app
    from app.core.database import get_db
    app.dependency_overrides[get_db] = lambda: test_db
    yield TestClient(app)
    app.dependency_overrides.clear()
```

**`auth_headers` fixture** — calls `POST /api/auth/login` with test credentials to get a real JWT:
```python
@pytest.fixture
def auth_headers(client):
    resp = client.post("/api/auth/login", json={
        "username": os.environ["ADMIN_USERNAME"],
        "password": os.environ["ADMIN_PASSWORD"],
    })
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
```
No auth mocking — this exercises the real JWT flow.

---

## Test Patterns

### Service tests
Each service test file follows:
1. **Happy path** — create entity via service, assert fields match input
2. **Not-found** — `get_by_id(9999)` returns `None`
3. **Error path** — duplicate URL raises `ValueError`; invalid data handled gracefully

### `scraper_service` tests
- `normalize_date` tested as a pure function (no DB)
- `deactivate_past_events` uses `test_db` with seeded past/future events
- `process_scraped_events` patches `SessionLocal` to return the test DB session

### API tests
1. Seed data directly into SQLite via `test_db`
2. Call endpoint via `client`
3. Assert HTTP status + response shape (not exact values)
4. Admin-only routes tested twice: without `auth_headers` (expect 401/403) and with (expect 2xx)

---

## Coverage Gate

`--cov-fail-under=70` in `pytest.ini`. CI fails if coverage drops below 70%.  
Codecov upload remains `continue-on-error: true` (visibility only, not a gate).

---

## Out of Scope

- `tests/integration/test_scrapers_real.py` (live network calls) — stays excluded via `-m "not integration"`
- New GitHub Actions workflow file — not needed; existing workflow picks up `pytest.ini` addopts
- Social media / community templates — separate prompt (Bölüm 1/3)
- Post-deploy smoke tests — separate prompt (Bölüm 4)
