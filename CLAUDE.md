# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TechEventRadar aggregates Turkish tech events (hackathons, workshops, seminars) from multiple platforms into a single site. Scrapers pull data automatically; the backend exposes it via REST; the frontend consumes `/api`.

Stack: **FastAPI + SQLAlchemy + PostgreSQL + React (Vite) + Docker Compose**

## Commands

### Docker (primary workflow)
```bash
# First run: copy env, then start
cp .env.example .env   # edit SECRET_KEY (≥32 chars), ADMIN_USERNAME, ADMIN_PASSWORD
docker-compose down && docker-compose up -d --build

# Restart after .env changes (v1 docker-compose requires full down+up, not just restart)
docker-compose down && docker-compose up -d
```

Services: Frontend `http://localhost:3000` · Backend `http://localhost:8000` · Swagger `http://localhost:8000/docs`

### Backend (local)
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend (local)
```bash
cd frontend && npm install && npm run dev
```

### Database migrations
```bash
alembic upgrade head
alembic revision --autogenerate -m "description"
alembic downgrade -1
```
`DATABASE_URL` env var takes precedence over `alembic.ini`'s `sqlalchemy.url`.

### Tests
```bash
pytest                                    # all tests (requires --cov ≥70%)
pytest -m "not integration"              # skip integration tests
pytest tests/test_foo.py::test_bar -v    # single test
```

### Manual scrape
```bash
docker-compose run --rm scraper python scripts/run_daily_scrape.py
```

## Architecture

### Backend (`app/`)

```
app/
  main.py          — FastAPI app, CORS, traffic-logging middleware, startup hook
  core/
    config.py      — Pydantic Settings; raises on boot if SECRET_KEY <32 chars or creds missing
    database.py    — SQLAlchemy engine + SessionLocal + Base
    auth.py        — HTTPBearer dependency (get_current_admin)
  api/
    __init__.py    — mounts public_router at /api, admin_router at /api/admin
    public.py      — unauthenticated endpoints (events, announcements, event-requests, suggestions)
    admin.py       — protected endpoints (CRUD, scraper control, analytics, notifications)
  models/          — SQLAlchemy ORM models (one file per entity)
  schemas/         — Pydantic request/response schemas
  services/        — business logic (event_service, auth_service, scraper_service, analytics_service, …)
  scrapers/        — one scraper per source; driver_utils.py wraps Selenium/Chromedriver
```

**Auth flow:** `POST /api/admin/login` → JWT → `Authorization: Bearer <token>` on all `/api/admin/*` calls. Token stored in `localStorage` on the frontend; a 401 fires a `auth:logout` custom event to clear it.

**Traffic logging:** HTTP middleware in `main.py` logs every successful non-admin, non-static request to `traffic_log` via `AnalyticsService`. Skips OPTIONS, /docs, /openapi.json, /api/admin.

**Scraper `profiles`:** The `scraper` service in `docker-compose.yml` has `profiles: [scraper]` so it only runs on explicit `--profile scraper` or `run --rm scraper`.

### Frontend (`frontend/src/`)

```
main.jsx        — React 18, BrowserRouter, react-query QueryClient, ThemeProvider > AuthProvider
App.jsx         — lazy-loaded Routes; ProtectedRoute wraps all /admin/* paths
contexts/
  AuthContext   — JWT storage, login/logout, 'auth:logout' event listener
  ThemeContext  — dark/light toggle, persisted via localStorage, sets data-theme on <html>
services/api.js — single axios instance (baseURL: /api); auth interceptor; publicAPI / adminAPI / formAPI
pages/          — one file per route; admin pages live alongside public ones
components/     — shared UI (Header, Footer, EventCard, etc.); admin sub-components in components/admin/
```

**Styling:** Single `index.css` with CSS custom properties (`--bg-primary`, `--action-primary`, etc.) for theming; Bootstrap grid classes for layout; no CSS modules. Light theme overrides via `[data-theme="light"]`.

**API proxy:** Vite dev server proxies `/api → http://backend:8000` (`vite.config.js`). In production this is handled at the reverse proxy level — do not change `baseURL: '/api'`.

## Key Constraints

- `SECRET_KEY` must be ≥ 32 characters; `ADMIN_USERNAME` and `ADMIN_PASSWORD` must be set. The app refuses to start otherwise (bypassed only with `ALLOW_INSECURE_DEFAULTS=true`).
- `frontend/package.json` and `frontend/package-lock.json` are tracked explicitly despite the general `*.json` ignore rule; use `npm ci` for reproducible installs.
- Old `docker-compose` v1.29 has a `ContainerConfig` bug: always use `down && up`, never just `up` when recreating containers.
- JSON responses use `UnicodeJSONResponse` (ensure_ascii=False) — do not replace with standard `JSONResponse`.

## Agent skills

### Issue tracker

İşler `.scratch/<feature>/` altında yerel markdown dosyalarıyla takip edilir. GitHub Issues kullanılmaz. Ayrıntılar: `docs/agents/issue-tracker.md`.

### Triage labels

Varsayılan yerel durumlar kullanılır: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. Ayrıntılar: `docs/agents/triage-labels.md`.

### Domain docs

Tek bağlam kullanılır: kökte `CONTEXT.md`, mimari kararlar için `docs/adr/`. Ayrıntılar: `docs/agents/domain.md`.

<!-- METO-AI:CLAUDE_ADAPTER:BEGIN -->
@AGENTS.md

# Claude Code repository adapter

- Load the active task before source changes.
- Use `.claude/agents/` for specialized roles.
- Architects write plans, not production code.
- Reviewers report findings, not production-code changes.
- Before ending incomplete work, update task state and continuation context.
<!-- METO-AI:CLAUDE_ADAPTER:END -->
