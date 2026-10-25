# ADR-0008: Per-URL <head> via nginx SSI + backend fragment

## Status

Accepted — 2026-10-25. Supersedes the "serve one static shell" behaviour; does not
replace ADR-0006's prerender PoC (that targets first paint, this targets crawlers).

## Context

The SPA served the same 5 KB shell for every URL: generic title, `canonical` = home,
default Open Graph tags, no Event JSON-LD. Page-specific tags only appeared after
JavaScript ran, so non-rendering crawlers and link previews saw every page as the
home page, and unknown URLs answered 200 without `noindex`. Build-time prerender
cannot fix this in production: the Docker build has no backend/API, and a snapshot
would freeze event lists at deploy time.

## Decision

`index.html` contains an nginx SSI `include` of `/_seo$seo_orig`. nginx maps that to
`GET /api/seo/head/<path>` on the backend, which returns the `<head>` tags for that
URL (`app/services/seo_head.py`): title, description, robots, canonical, `og:*`,
`twitter:*` and, for events, Event + Breadcrumb JSON-LD. The default tags live in a
`seo_default` SSI block that nginx outputs as the stub when the backend is down,
slow (2 s timeout) or answers an error; without SSI (vite dev/preview, prerender) the
directives are plain comments and the block is part of the page.

Unknown paths, inactive/past events and unpublished posts get `noindex, follow` and
no canonical. Events without a date get no Event JSON-LD (Google requires
`startDate`); `startDate` is the stored naive local time, which Google reads as local
to the event. The client-side JSON-LD uses the same naive value.

## Consequences

- One extra backend request per HTML page view (not written to `traffic_log`; the
  middleware skips `/api/seo/`). Cheap query, no cache yet (`shortcut:` add a small
  TTL cache if load grows).
- HTTP status is still 200 for unknown URLs (SSI cannot change it); `noindex` covers it.
  A real 404 needs the backend to serve the shell (not done).
- Titles/descriptions for static pages are duplicated in `STATIC_PAGES` and the React
  pages; drift is possible. Update both when a page's SEO text changes.
- `ssi on` is scoped to `location = /index.html`, so API/backend HTML is never parsed.
  Included text is escaped (`html.escape`, JSON-LD `<`/`>`/`&` escapes), and the
  subrequest location is `internal`.
- Deploy order is safe either way: if the new frontend runs against an old backend the
  subrequest 404s and nginx falls back to the default tags.
- Verified locally with the real nginx image and the real backend module: per-URL
  tags, noindex cases, backend down (instant fallback), backend hung (2 s then
  fallback). Not verified: behaviour behind the production host nginx.
