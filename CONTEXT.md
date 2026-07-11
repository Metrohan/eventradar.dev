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
