# ADR-0006: Generated Event Cards Instead of Source Images

## Status

Accepted — 2026-10-25. Supersedes the image fetch/resize step of ADR-0005.

## Context

ADR-0005 downloaded each source site's event image, re-encoded it to a 400x200
WebP and served it from our own domain; the frontend also hotlinked
`image_url` (detail page, OG image, JSON-LD) and the Telegram notifier sent it
with `sendPhoto`. Several sources' terms (e.g. Patika, Youthall) forbid copying
or re-publishing their content, and event images are the part most likely to be
protected as a work. Adding any revenue to the site raises that risk further.

## Decision

Never fetch, store, link or forward a source image. Every event gets a card
rendered from facts only (title, date, location, source name) with Pillow and
Liberation Sans (`fonts-liberation`, already in the image for Chrome), cached by
a hash of those facts (`_RENDER_VERSION` is part of the key). The card replaces
the thumbnail at the same size, storage and URL prefix as ADR-0005; the SSRF /
host-allowlist code is deleted because nothing is fetched any more.

## Consequences

- No third-party image leaves the source site through us; scraped `image_url`
  stays in the database column but is unused (dropping it is a separate task).
- Telegram notifications are text-only; the event detail page shows no image
  (the card would only repeat the title below it); OG image / JSON-LD use the card.
- Existing events keep their old copied thumbnails until the next scrape updates
  them; old files stay on disk until removed (human-approved cleanup).
- Cards look the same across sources by design; accent hue is derived from the
  source name, with no logos or brand assets.

## Follow-ups (code done; the production run is a separate, human-run step)

- The public API (`GET /api/events`, `GET /api/events/{id}`) no longer returns
  `image_url`; the admin schema keeps it for the edit form. The DB column and the
  scrapers' `image_url` stay (dropping them is a separate migration).
- Old copied thumbnails: `scripts/backfill_event_cards.py` re-points every event at
  its card and MOVES unreferenced files to `--archive-dir` (never deletes; the
  archive must be outside the served directory). Dry-run by default. Run order on
  the server: DB dump -> dry-run -> `--apply --archive-dir <path>` -> copy the archive
  out of the container (a redeploy erases container-local paths) -> delete it after
  a few days if nothing is missed.
- Scraped text is capped at 300 characters before hashing and drawing, so a huge
  `location` cannot make rendering slow.
