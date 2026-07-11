# ADR-0001: Canonical Source Catalog

## Status

Accepted — 2026-07-11

## Context

Source names and capabilities were repeated across daily scraping, manual scraper triggers, frontend lists, card styles, and documentation. Adding Tech Istanbul exposed drift between these copies.

## Decision

Maintain one backend Source Catalog containing each integration's stable key, public name, website, runner mode, enabled state, and private runner implementation.

Daily and manual scraping use the same catalog. A public `/api/sources` interface exposes enabled source metadata without runner implementation details. Enabled sources remain visible even without current events or during temporary scraper failures.

Frontend colours are derived from the stable source key rather than stored in the catalog.

## Consequences

- Adding or disabling an integration is localized to the Source Catalog.
- Public source displays can stay consistent with backend capabilities.
- Frontend source lists require the backend interface to be available.
- Curated educational-resource lists may remain separate when they describe resources that are not scraper integrations.
