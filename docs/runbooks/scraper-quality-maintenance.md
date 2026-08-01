# Runbook: Scraper Quality Panel Maintenance

Covers `/admin/quality` (`frontend/src/pages/QualityPage.jsx`, backed by
`app/services/source_quality.py`) — what each column means, what triggers
an automatic alert, and what to actually do when a source looks unhealthy.

## Reading the panel

| Column | Computed from | Meaning |
|---|---|---|
| **Başarı** (success rate) | Last 20 `ScraperLog` rows for the source, `% status == "success"` | `Veri yok` (no data) means the source has never run, not that it's broken |
| **Tamlık** (completeness) | `% of (date, location, description) fields present across all stored events for that source` | Low completeness means the *scraper's parsing logic* is missing fields, not that the source is failing to run |
| **Aktif / Toplam** | `is_active=True` count / total stored events for that source | A source can have a healthy success rate but very few active events simply because it has few current listings |
| **Eksikler** (missing) | Per-field missing counts | Points at which extraction step to look at first (date parsing vs. location parsing vs. description) |
| **Son durum** (last status) + consecutive failures + last error | Most recent `ScraperLog` row, and a walk-back-from-most-recent count of consecutive `status == "failed"` rows | This is what actually triggers the Telegram alert (see below) |

**Completeness and success rate measure different failure modes — don't
conflate them.** A source can be at 100% success rate (the scraper runs
without throwing) and 40% completeness (it runs fine but its HTML
selectors miss the date field on half the listings). Low completeness is
a scraper *parsing* bug, not a scraper *availability* problem — check the
relevant `app/scrapers/<source>_scraper.py`, not the source's website
uptime.

## Automatic alerting (already wired, no action needed to enable)

`app/services/scrape_run.py`'s `ScrapeRunCoordinator` fires a Telegram
alert (`telegram_service.notify_scraper_failure`) the **first time** a
source's consecutive failure count hits the threshold (default: **3**,
`failure_alert_threshold` in `ScrapeRunCoordinator.__init__`) — it does
not re-alert on every failure past that, only the crossing. If a source
has been silently failing for a while with no alert, check: is
`TELEGRAM_BOT_TOKEN`/`TELEGRAM_CHANNEL_ID` actually configured (`
telegram_service._is_configured()`), and did the failure count actually
reach 3, or is it flapping (fail, succeed, fail — never 3 in a row)?

## When a source shows consecutive failures

1. Check `last_error` in the panel (or `ScraperLog.error_message` directly)
   — this is the actual exception message from the scraper run, usually
   enough to tell whether it's a selector break (site changed its HTML),
   a network/timeout issue, or a Cloudflare/anti-bot block (see
   `docs/adr/...` and existing memory notes on Coderspace's Cloudflare
   history for what that looks like: `cloudflare` appearing in page text
   is not always a real block — false positives happen from CDN script
   tags, verify by checking whether the actual event data came back).
2. Reproduce locally/manually:
   ```bash
   docker compose exec backend python scripts/run_daily_scrape.py
   # or, for one source only, use the admin panel's manual "Run" action
   # (ScraperControlPage), which calls the same runner
   ```
3. If it's a genuine site change (selector broke): fix the scraper, add
   or update the relevant `tests/unit/test_<source>_scraper.py` fixture
   if one exists, redeploy.
4. If the source is temporarily down/blocking and there's no immediate
   fix: **don't silently let it keep alerting** — either fix promptly or
   disable it in `app/services/source_catalog.py` (`enabled=False` on its
   `SourceDefinition`) so it stops running and stops contributing failed
   `ScraperLog` rows, and re-enable once fixed. Disabling is a code
   change + deploy, not a runtime toggle — there's no admin UI for it,
   intentionally, so it's always a reviewed, committed decision.
5. After a fix, watch the panel for the next scheduled run (see crontab:
   daily at 05:00, per `docs/runbooks` server config) or trigger a manual
   run to confirm before considering it resolved.

## When completeness drops for a previously-healthy source

This means the source changed its page structure but not enough to break
the whole scrape (title/URL extraction still works, so `status` stays
`success`) — only some fields silently return `None`/empty. This is the
*quieter*, more dangerous failure mode because it doesn't alert. Treat a
sudden completeness drop on the panel the same as a failure: open the
relevant scraper file, diff its selectors against the source's current
HTML, and fix the specific field extraction that broke.
