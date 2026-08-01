# Runbook: External Uptime Monitoring

## Decision

**Service: UptimeRobot** (free tier). Reasoning:

- Free tier covers this project's needs: 50 monitors, 5-minute check
  interval, Telegram/email/webhook alert delivery — no paid plan needed.
- The alternative considered, **Healthchecks.io**, is built around the
  "dead man's switch" pattern (a *scheduled job* pings it; silence means
  failure) — a better fit for monitoring that the daily scraper cron
  actually ran than for monitoring an HTTP endpoint's uptime. Worth
  adding *later* for `scripts/run_daily_scrape.py`'s cron specifically,
  but that's a separate decision from "is the site up," which is what
  this runbook covers.
- Requires no code changes to add a monitor — this stays entirely outside
  the app, which is the point of "external" monitoring (it must not
  depend on the thing it's checking).

**This runbook does not create the UptimeRobot account** — that needs a
real email/login only the project owner should provide. What's done here:
fixed a real gap that would have made monitoring `/health` meaningless
(see below), and documented the exact setup steps.

## Fixed before this could work: `/health` wasn't actually reachable externally

`app/main.py`'s `/health` endpoint was never proxied by nginx
(`frontend/nginx.conf` only proxied `/api/`, `/sitemap.xml`, `/media/`).
A request to `https://eventradar.dev/health` fell through to the SPA
fallback (`try_files ... /index.html`) and returned a **200 with the
homepage HTML** — meaning an uptime monitor watching that URL would keep
reporting "up" even with the backend fully down. This is now fixed
(`location = /health` added to `nginx.conf`, proxying to the backend
exactly like `/api/`), verified against the pattern already used for the
other proxied paths.

## Setup steps (for whoever has UptimeRobot account access)

1. Create a free account at uptimerobot.com.
2. Add a new **HTTP(s)** monitor:
   - URL: `https://eventradar.dev/health`
   - Interval: 5 minutes (free tier minimum)
   - Expected response: the monitor should be configured to require
     HTTP 200 **and**, if UptimeRobot's plan supports keyword matching,
     the response body containing `"healthy"` — the endpoint returns
     `{"status": "healthy", "message": "..."}`, so a plain 200 alone
     would still false-positive on some other proxy-level 200 (e.g., a
     misconfigured fallback). Keyword matching closes that gap.
3. Alert contact: Telegram is the established channel for this project
   (see `scripts/monitor_alerts.py`, and the deploy-failure notification
   added alongside this runbook). UptimeRobot supports a Telegram alert
   contact directly (Settings → Alert Contacts → Telegram) — point it at
   the same bot/chat already used for `TELEGRAM_CHAT_ID` so all
   operational alerts land in one place instead of fragmenting across
   channels.
4. Optional second monitor: `https://eventradar.dev/` (the homepage
   itself) — catches nginx/frontend-container outages that a
   backend-only `/health` check wouldn't (e.g., frontend container down
   but backend still up would pass `/health` and fail this one).

## Why this belongs outside the app

`scripts/verify_deploy.sh` and `deploy.yml`'s rollback already check
health *from the same server*, right after a deploy — that only proves
the app started, not that it's still reachable from the outside (DNS,
firewall, the whole server being down, nginx misconfigured, etc. are all
invisible to a same-host check). External monitoring is the only way to
catch "the server is unreachable from the internet," which is exactly the
failure mode a same-host check structurally cannot detect.
