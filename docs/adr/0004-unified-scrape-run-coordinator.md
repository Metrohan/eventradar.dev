# ADR-0004: Unified Scrape Run Coordinator

## Status

Accepted — 2026-07-12

## Context

Cron logged before ingestion with `new_events=0`, while manual runs parsed formatted strings after ingestion. The `all` path used a subprocess and produced different semantics from a single-source run.

## Decision

Use `ScrapeRunCoordinator` for both cron and manual triggers. One run performs fetch, typed ingestion, source reconciliation, and one final log write. The typed result carries all run metrics and error state.

## Consequences

- Run metrics have one meaning across every caller.
- Failed fetches never reconcile source data.
- The subprocess path is removed.
- Scraper logs gain updated, failed, and deactivated counters.
