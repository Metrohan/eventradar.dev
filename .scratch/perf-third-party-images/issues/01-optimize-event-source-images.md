# Optimize/proxy oversized third-party event images

Status: needs-triage
GitHub: https://github.com/Metrohan/eventradar.dev/issues/76

## Context

PageSpeed Insights (via Google Search Console, 2026-07-17) flagged "Çok büyük
ağ yükleri" on both desktop (~6.9 MB total) and mobile (~10.1 MB total) for
`https://eventradar.dev/`. The large payload is almost entirely event
thumbnail images pulled directly from source platforms and rendered
unmodified in `EventCard` (`frontend/src/components/EventCard.jsx`):

- `cdn.prod.website-files.com` — two PNGs at 2.0 MB and 1.35 MB
- `api.ibb.gov.tr` — up to four PNGs, largest at 0.9-2.3 MB
- `learn.pupilica.com` — several images 300-480 KB each
- `framerusercontent.com`, S3 buckets — additional 100 KB-1 MB images

These are `event.image_url` values scraped as-is from each source
(`app/scrapers/*.py`) and stored in the `events.image_url` column
(`app/models/event.py`). The frontend already displays them at a fixed
200px-tall card thumbnail (`.event-image` in `frontend/src/index.css`) with
`loading="lazy"`, but the full multi-megabyte original is still downloaded —
lazy-loading only delays the request, it doesn't shrink it.

## Why this is a separate issue

Fixing this requires either:
1. An image proxy/resizing service (e.g. an on-the-fly resize endpoint in the
   FastAPI backend, or a CDN-level image transform) that re-encodes source
   images to a card-appropriate size before serving them, or
2. Downloading and caching a resized copy at scrape time in
   `app/scrapers/*.py` / `app/services/scraper_service.py`.

Both are a real backend/infra design decision (storage, cache invalidation,
handling source images disappearing) — out of scope for the nginx/CSS/CLS
fixes already shipped in `fix/google-search-console`.

## Suggested approach (not decided)

- Add a lightweight resize step in the scraper pipeline that downloads
  `image_url`, re-encodes to e.g. 400x200 WebP, and stores it (S3/local
  volume) behind the app's own domain — this also removes the current
  dependency on third-party hosts staying up.
- Alternatively, front `image_url` with a resize proxy
  (`/api/img?url=...&w=400&h=200`) that streams a transformed image with
  caching headers.

## Acceptance criteria

- [ ] Event card thumbnails on the homepage/listing pages are served at a
      size proportionate to their 400x200 display box (not multi-MB
      originals).
- [ ] Total network payload for the homepage drops meaningfully in a fresh
      PageSpeed Insights run (large network payload audit).
- [ ] Broken/unreachable source images still fall back to
      `/placeholder-image-colored.webp` (existing `onError` behavior in
      `EventCard.jsx` must keep working).
