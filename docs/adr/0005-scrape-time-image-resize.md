# ADR-0005: Scrape-Time Thumbnail Resize

## Status

Accepted — 2026-07-31

## Context

Issue #76: PageSpeed Insights flagged event thumbnails as the dominant
contributor to homepage payload (~6.9 MB desktop / ~10.1 MB mobile,
2026-07-17 run). `EventCard` renders `event.image_url` — the original,
unmodified source image (up to 2.3 MB per file) — into a 400x200 CSS box.
Two architectures were considered to fix this:

**A) Scrape-time resize.** During ingestion, download the source image once,
re-encode it to 400x200 WebP, and cache it on disk behind the app's own
domain.

- (+) No dependency on third-party hosts staying up at request time.
- (+) Zero added runtime latency — the transform already happened when the
  event was scraped.
- (–) Needs a storage location and a cache-invalidation rule.
- (–) A source image that changes without the URL changing won't be
  detected (accepted limitation — see Consequences).

**B) On-demand resize proxy** (`/api/img?url=...&w=400&h=200`).

- (+) No storage; always reflects the current source image.
- (+) Smaller code change — one endpoint, scrapers untouched.
- (–) Every uncached request depends on a third-party host being up; that
  host's outage becomes this app's outage.
- (–) Needs its own cache layer to avoid re-fetching/re-encoding on every
  request, at which point most of B's simplicity advantage over A is gone.

## Decision

**Scrape-time resize (A)**, because it removes the third-party
availability dependency and adds no runtime cost — the two properties that
matter most for a page whose thumbnails are read far more often than the
underlying event data changes.

**Storage:** a local Docker named volume (`thumbnail_data`, mounted at
`/app/data/thumbnails`), not S3. The project runs on a single VPS with no
existing object-storage credentials or infrastructure; a local volume
needs no new dependency and matches the existing `postgres_data` pattern.
Revisit if the deployment ever needs to scale beyond one host.

**Format:** WebP only (no AVIF fallback). WebP is supported by all
current browser targets (including Safari 14+) and directly satisfies
issue #76's acceptance criteria ("400x200 WebP"). AVIF's smaller output
wasn't judged worth the added encode time and `<picture>`-fallback
complexity for a 400x200 thumbnail.

**Fetch security:** see `app/services/image_pipeline.py`.

- HTTPS-only, and the hostname must match `ALLOWED_IMAGE_HOST_SUFFIXES` —
  a coarse allowlist derived from the domains scrapers actually construct
  image URLs from, plus the third-party CDNs (Webflow, Framer) issue #76
  observed in production data.
- The hostname is resolved and every returned IP must be public (rejects
  private/loopback/link-local/multicast/reserved ranges) — this is the
  actual SSRF defense; the allowlist above is a coarse filter on top of it,
  not a substitute.
- Response must be `Content-Type: image/*`, `200` (no redirect-following),
  and capped at `MAX_IMAGE_BYTES` (8 MB) enforced by streaming byte-count,
  not by trusting `Content-Length`.

**Cache key:** `sha256(source_image_url)[:24]`. A cache hit is a file-exists
check (no network call); a cache miss fetches, validates, resizes, and
writes once. If an event's `image_url` changes, the new URL hashes to a
new filename, so the new thumbnail is generated automatically and the old
file is simply orphaned (not deleted — see Consequences).

## Consequences

- `events.thumbnail_url` is nullable and only ever set by the scrape
  ingestion path (`app/services/event_ingestion.py`); admin-created events
  (`EventCreate`/`EventUpdate`) don't go through this pipeline and keep
  using `image_url` directly — out of scope for issue #76, which is about
  scraped thumbnails.
- Frontend fallback chain is `thumbnail_url → image_url → placeholder`
  (`EventCard.jsx`), so a failed/skipped thumbnail degrades to prior
  behavior rather than breaking the card.
- **Known limitation — stale content at a stable URL.** If a source site
  swaps the image behind an unchanged `image_url`, this pipeline keeps
  serving the old cached thumbnail indefinitely (no periodic re-fetch).
  Judged acceptable: none of the 13 scraper sources are known to do this,
  and the failure mode is a stale-but-valid thumbnail, not a broken one.
- **Known limitation — orphaned files.** Thumbnails are never deleted, so
  disk usage grows monotonically with distinct `image_url`s ever seen.
  Accepted for now given the current event volume; revisit with a cleanup
  job if disk pressure becomes real.
- **Known limitation — DNS-rebinding.** The IP-validation check resolves
  DNS at validation time, not at connection time, so it doesn't defend
  against DNS rebinding between check and fetch. Accepted because the
  target hostname is additionally constrained by the static allowlist —
  an attacker would need to control DNS for an already-trusted source
  domain, which is a larger compromise than this pipeline can reasonably
  defend against.
- The allowlist needs manual maintenance when a source site changes CDN
  providers; a legitimate image on an unlisted host silently falls back
  to `image_url`/placeholder rather than hard-failing the scrape.
