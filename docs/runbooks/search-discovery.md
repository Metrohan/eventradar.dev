# Search discovery rollout (TASK-102)

## Current account state
No GA4 measurement ID, Google verification or Bing verification tags were found in
tracked frontend code. This is not proof accounts do not exist. Owner does not know.
No account, DNS, verification, analytics tag, production migration or deploy changed.

## Publication gates
PR #105 is already merged as fdf8478; this task is based on that lifecycle column.
Before starting the new backend run `alembic upgrade head` with a reviewed backup and
explicit production approval. New unique non-null slug column is required. Existing
rows become `/events/etkinlik-ID`; new rows receive a title-based immutable slug.
Do not recompute slugs on title edits. Downgrade discards permalinks: preserve a URL
mapping backup first. App-only rollback retains the column and its database default: old writers can still
insert events. PostgreSQL >=13 is required for the built-in gen_random_uuid().
The migration is transactional; backfill and NOT NULL take a table lock, so schedule
a reviewed deployment window. Validate old-style inserts before restarting writers.

Nginx serves `/events/*`, legacy `/etkinlik/ID`, `/kategoriler*`, `/sehirler*` through
the backend. These are full HTML documents for all user agents. There is no bot-only
rendering. Old pages return 301; hidden/missing return 404; expired public history
returns 200/noindex without Event markup. Application closure does not mean event cancellation.

## Google Search Console
Owner signs into https://search.google.com/search-console and checks for an existing
`eventradar.dev` Domain property or `https://eventradar.dev/` URL-prefix property.
Prefer Domain property using Google's DNS TXT verification through the domain owner.
Do not create duplicate properties or paste credentials into the repository.
After verification/deployment, submit `https://eventradar.dev/sitemap.xml`.
Use URL Inspection on one active event, an old-ID redirect and a past event. Confirm
rendered title/content/canonical, 301 destination, and noindex respectively.
Validate an eligible event with https://search.google.com/test/rich-results .
Unknown date/location/organizer facts are not invented; not every event qualifies
for a rich result. Organization describes EventRadar, not the source aggregator as
an assumed event organizer or performer.

## Bing Webmaster Tools
Owner signs into https://www.bing.com/webmasters and checks existing sites. Import
an owned Search Console property, or use Bing's DNS verification when needed.
Submit the same canonical sitemap and inspect a real active-event slug after rollout.
Do not add fake verification values or automatically submit every legacy URL.

## GA4: AI-source reporting
Check https://analytics.google.com for an existing EventRadar property/web stream.
A property ID/measurement ID and permission to change the account are needed; do
not install a second tag until an existing tag/container has been ruled out.
No GA4 tracking is installed by this task because property and consent configuration
are unknown. Native analytics currently counts requests; it is not a GA4 session report.

In GA4 Traffic acquisition, use Session source / medium and landing page dimensions;
compare the last 28 days with the preceding period, with sessions, engaged sessions,
engagement rate and key events. Check the built-in AI Assistant channel first. If
coverage is insufficient, create a custom channel group above Referral using Source
matches regex:

```text
^([a-z0-9-]+\.)*(chatgpt\.com|chat\.openai\.com|claude\.ai|perplexity\.ai|gemini\.google\.com|copilot\.microsoft\.com|grok\.com|chat\.deepseek\.com|chat\.mistral\.ai)$
```

Keep individual sources visible so ChatGPT can be compared with other assistants.
Do not classify all google/bing traffic as AI; no-referrer traffic remains unattributed.
UTM-tagged source values and provider domains can change; review observed values.
Record actual results only after owner grants access and real session data exists.

Sources checked 2026-10-30:
- https://developers.google.com/search/docs/appearance/structured-data/event
- https://support.google.com/analytics/answer/13051316
- https://support.google.com/analytics/answer/9756891

## UI boundary
New detail and collection documents are standalone Turkish server-rendered pages.
They preserve core content, generated card image, source access, collection navigation
and share links. The previous SPA theme/language widgets are not mounted in these
documents; full visual and language parity is a publication review item. SPA listing
navigation remains localized. Date-only versus explicit midnight is ambiguous in
the legacy datetime schema; midnight retains end-of-day semantics. Existing rows
with incorrectly inferred dates are not bulk-rewritten without verified source data.

Development/preview retains the existing legacy-ID SPA route for frontend regression
coverage; canonical `/events/*` and collection documents proxy to the backend.
The production nginx additionally handles legacy ID redirects.
Run real-backend no-JS/browser checks with `PRERENDER_CHROMIUM_PATH=/usr/bin/chromium-browser python scripts/check_discovery_browser.py` after the frontend build.

## Owner clarification and public audit (2026-10-30)
Owner confirms Google Search Console configuration is already complete. Do not
repeat initial setup. Bing status and GA4 access remain unconfirmed.
Public HTTP checks:robots200 with sitemap declaration and public crawling allowed;
sitemap200,valid XML,61 URL entries. Home,hackathon landing and sample event402
each have one description,one og:title,and canonical/og:url agree. Event402 still
has no server-rendered h1,confirming local SSR changes are not deployed.
Observed duplicated Content-Type on robots and sitemap. Removed redundant sitemap
Content-Type addition from the repository host-nginx example. Actual host nginx
configuration still needs a separately approved rollout; no live change performed.
