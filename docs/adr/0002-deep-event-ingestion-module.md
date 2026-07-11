# ADR-0002: Deep Event Ingestion Module

## Status

Accepted — 2026-07-11

## Context

Scraped-event normalization, persistence, lifecycle policy, tag classification, transaction handling, result formatting, and Telegram delivery lived in one function with a global database dependency. Daily and manual callers parsed formatted strings to recover counts.

## Decision

Introduce a deep `EventIngestion` module with canonical `ScrapedEvent` input and typed `IngestionResult` output.

The module owns transaction and lifecycle implementation. Database sessions and post-commit notifications are injected adapters. Transaction failures raise `IngestionError`; individual record failures and notification failures are represented in the result.

## Consequences

- Daily and manual scraping share one typed interface.
- Tests can exercise the same seam as production callers without patching global session factories.
- Notification delivery cannot roll back committed event data.
- Scraper adapters must convert their mappings to `ScrapedEvent` before ingestion.
