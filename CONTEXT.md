# EventRadar Domain Context

## Source Catalog

The **Source Catalog** is the canonical registry of event-source integrations. A source has a stable key, public name, website, runner mode, enabled state, and an internal scraper runner.

- `enabled=true` sources remain publicly visible even when they have no current events or their latest run failed.
- Runner implementations stay private; public callers receive only source metadata.
- Static and browser runner modes determine execution ordering, not public availability.
- Frontend colour is presentation data and is derived deterministically from the stable source key.

Avoid maintaining independent source-name arrays in backend orchestration or frontend screens.

## Event Ingestion

**Event Ingestion** converts scraper payloads into canonical `ScrapedEvent` values, persists them, applies active-event lifecycle rules, classifies tags, and publishes post-commit notifications.

- Scraper adapters own extraction only; they do not own persistence rules.
- `EventIngestion.ingest()` returns a typed `IngestionResult` rather than a formatted status string.
- A failed transaction raises `IngestionError`; individual invalid records are reported in the result.
- Notifications run after commit and remain non-fatal.
- Database sessions and notifications are adapters behind explicit seams.

## Source Reconciliation

**Source Reconciliation** retires events that a successful source run has stopped observing.

- `last_seen_at` records when Event Ingestion most recently observed an event.
- Reconciliation runs only after a successful source run; failed runs never retire data.
- A three-day grace period absorbs temporary empty or partial source responses.
- Reconciliation is source-scoped and never affects another Source Catalog entry.

## Source Quality

**Source Quality** combines recent run health with event-data completeness for each enabled Source Catalog entry. Success rate, consecutive failures, last error, and missing date/location/description counts are computed behind one interface and displayed in the admin area.

## Scrape Run

A **Scrape Run** is one source fetch followed by Event Ingestion, Source Reconciliation, and a single persisted outcome. `ScrapeRunResult` records fetched, new, updated, failed, and deactivated counts with duration and error state. Cron and manual triggers use the same coordinator interface.

Source fetch uses bounded exponential retry. Only extraction is retried; Event Ingestion and database operations run once to avoid duplicate side effects.

## Migration Contract

The **Migration Contract** requires a blank database to upgrade through the complete Alembic chain to the current head. CI verifies this independently from SQLAlchemy `create_all()` so missing historical tables cannot be hidden by application startup.
