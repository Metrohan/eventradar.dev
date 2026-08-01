# Lessons Learned: Migrations, Notifications, Production Incidents

Grounded in this repo's actual history (git log, code, and prior session
notes) — not a generic best-practices list. Each entry names the real
commit/incident it comes from.

## Migrations

### `connection.exec_driver_sql()` silently doesn't bind SQLAlchemy-style parameters

`alembic/versions/e5f6a7b8c9d0_normalize_existing_locations.py` originally
used `connection.exec_driver_sql(f"UPDATE events SET location = :canonical WHERE ...", parameters)`.
`exec_driver_sql` passes SQL straight to the underlying DBAPI driver,
bypassing SQLAlchemy's parameter-binding layer — `:canonical`-style named
placeholders are a SQLAlchemy `text()` construct, not something the raw
driver understands. Fixed (commit `a32dd58` and its merge) by switching to
`connection.execute(text(f"..."), parameters)`.
**Lesson:** `exec_driver_sql` is for literal, pre-formatted SQL with no
SQLAlchemy-level parameter binding. Any migration that needs bound
parameters must use `connection.execute(text(...), params)`.

### CI ran migrations against SQLite only, hiding Postgres-specific issues

Before Faz 1, `test.yml`'s migration smoke test ran against
`sqlite:///./migration-smoke.db` — but production runs Postgres 16.
SQLite is far more permissive about type coercion, constraint enforcement,
and some SQL syntax differences (e.g., `ALTER COLUMN` semantics), so a
migration could pass CI on SQLite and still fail against real Postgres.
Fixed by adding a real `postgres:16` service container to the `test` job
and pointing the migration smoke test at it (see `.github/workflows/test.yml`).
**Lesson:** "migrations pass CI" only means what CI actually tests against
— matching the production database engine isn't optional if migrations
are meant to be trusted.

### Backup restores need matching role names, or ownership silently changes

From the 2026-08-01 restore drill (`docs/runbooks/restore-drill.md`):
`pg_dump`'s default output embeds `ALTER TABLE ... OWNER TO app_user`.
Restoring into a database whose connecting role isn't literally named
`app_user` prints one `ERROR: role "app_user" does not exist` per object
— non-fatal, the schema and data still restore completely, but every
object ends up owned by the restoring role instead. Not caught until the
first actual restore drill was run.
**Lesson:** a backup mechanism is unverified until it's been test-restored
at least once outside its origin environment — this exact class of gotcha
(works on the same host, surprises on a fresh one) is precisely what a
"do we have real backups" checklist misses if it only checks that the
dump file exists and has nonzero size.

## Notifications / PWA

### A service worker's `clients.claim()` reloaded the page for every first-time visitor

`frontend/public/sw.js`'s `activate` handler called `self.clients.claim()`.
Combined with `main.jsx`'s `window.location.reload()` on `'controllerchange'`
(a common pattern for "auto-reload when a new SW version takes over"),
`claim()`ing immediately fires `controllerchange` for the page that's
*currently loading* too, not just already-open tabs from a previous visit.
Every first-time visitor got a surprise full-page reload ~1-2s after their
first load — discovered while investigating an unrelated hydration bug
during the Faz 3 prerender PoC (`docs/adr/0006-prerender-poc.md`), not
through any monitoring or user report. Fixed by removing `clients.claim()`
— a new SW now only takes control on a client's *next* navigation.
**Lesson:** this specific `skipWaiting` + `clients.claim()` +
reload-on-controllerchange combination is a well-known PWA footgun
precisely because it's invisible without hydration/reload instrumentation
— it doesn't throw, doesn't log, doesn't fail a health check. It was found
by accident, not by process. Worth an explicit periodic check (e.g., watch
`framenavigated`/`load` event counts on a fresh page load) rather than
assuming "no error reports" means it's fine.

### Telegram message construction was designed defensively from the start

`app/services/telegram_service.py` HTML-escapes all interpolated content
(`html.escape()`) and validates URL schemes before sending — not a fix for
an incident, a design decision made up front because Telegram messages are
sent with `parse_mode: HTML` and event data (titles, descriptions) comes
from scraped third-party HTML, i.e., untrusted input. Included here as a
positive example, not just failures: the same "external content interpolated
into a structured message format" risk exists anywhere scraped data reaches
a template (Telegram messages, email digests, RSS) — worth checking each
new such integration against this pattern rather than re-deriving it.

## Production incidents

### ChromeDriver version mismatch when Chrome auto-updated

Scrapers hardcoded `version_main=144` for `undetected_chromedriver`. When
the server's Chrome auto-updated to 148, every Selenium-based scraper
started crashing (`app/scrapers/driver_utils.py`'s `create_uc_driver()`
now detects the installed Chrome's major version at runtime via
`get_chrome_major_version()` instead of a hardcoded constant — this
function still exists in the codebase, confirmed current). **Lesson:**
pinning a browser-automation driver version against an auto-updating
browser is a time bomb, not a stability measure — detect the actual
installed version at runtime instead of hardcoding what was true at
write-time.

### Server disk pressure from unbounded Docker build cache + zombie processes

Server disk usage reached 83% from accumulated Docker build cache and
dangling images; separately, 136 zombie Chrome processes had accumulated
from Selenium scraper runs that didn't clean up their browser processes on
crash/timeout. Resolved via manual cleanup (`docker system prune`-style
cache clearing, `journalctl --vacuum-size`, backend container restart to
clear zombie processes) rather than a systemic fix. **Open risk, not yet
addressed by any code change:** nothing currently prevents this from
recurring — there's no automated Docker cache pruning or Chrome zombie
process reaping. Worth a scheduled `docker system prune` and/or a
scraper-level safeguard (ensure the driver's `finally` block always calls
`.quit()`, and consider a watchdog for orphaned Chrome processes) as
follow-up work, not covered by this Faz.

### Coderspace Cloudflare false positives

The Coderspace scraper's Cloudflare-block detection matched on the literal
string `"cloudflare"` appearing anywhere in the page — but that string also
appears in ordinary CDN `<script>` tags on pages that loaded successfully,
not just on an actual Cloudflare challenge page. This caused the scraper to
report failures for runs that had actually succeeded. Fixed by switching to
`--headless=old` (less likely to trigger a real Cloudflare challenge in the
first place); current `app/scrapers/cs_scraper.py` has no
`"cloudflare"`-substring check left at all — the detection mechanism was
removed rather than replaced with a smarter one, and the scraper now just
extracts whatever cards it finds (logging the count) instead of trying to
pre-classify the page as blocked or not.
**Lesson:** detecting "did this get blocked" by substring-matching a
generic term is fragile enough that removing the check entirely and just
looking at actual extraction results was the right call — an indirect
textual signal that can appear for unrelated reasons is worse than no
signal at all.
