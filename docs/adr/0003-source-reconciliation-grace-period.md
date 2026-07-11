# ADR-0003: Source Reconciliation Grace Period

## Status

Accepted — 2026-07-11

## Context

Events without reliable dates cannot be retired by date comparison. Sources may also remove finished events, while temporary scraper failures or partial responses must not deactivate valid data.

## Decision

Record `last_seen_at` whenever Event Ingestion observes an event. After a successful source run, deactivate active events for that source only when their `last_seen_at` is older than three days.

Do not reconcile failed source runs. A successful empty run participates in reconciliation but still respects the grace period.

## Consequences

- Undated events eventually leave active listings after disappearing from their source.
- One transient incomplete response does not immediately deactivate data.
- Source names must use the canonical Source Catalog name.
- Retirement can lag source removal by up to three days.
