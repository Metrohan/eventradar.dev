# ADR-0006: Build-Time Prerender PoC for First Paint

## Status

Accepted (PoC scope only — see Consequences) — 2026-07-31

## Context

Issue #77: mobile PageSpeed scores Performance 52 with FCP 4.9s / LCP 5.0s,
almost entirely spent on "element render delay" (2.7s) — the SPA (Vite +
React, client-rendered, no SSR) paints nothing until the JS bundle
downloads, parses, executes, and React mounts. Issue #77's own comparison
already chose build-time prerendering over code-splitting alone, because
code-splitting reduces bundle size but doesn't remove the fundamental
"blank until JS boots" problem.

This ADR covers the PoC asked for in Faz 3: classify routes, prove
prerendering works for a representative set of them, and measure the
actual FCP/LCP/CLS/TBT effect — not a production rollout decision.

## Route classification

| Route | Class | Why |
|---|---|---|
| `/` | Static (public, DB-driven) | Same content for every visitor; content freshness bound by scrape cadence, not per-request |
| `/takvim` | Static (public, DB-driven) | Same as above |
| `/hackathonlar`, `/bootcamplar`, `/online-etkinlikler`, `/bu-haftaki-etkinlikler`, `/son-basvurular` | Static (public, DB-driven) | Same `EventListing` data source, filtered views |
| `/bootcamp-rehberi`, `/egitim-kaynaklari` | Static (public, mostly hand-authored) | No auth, rarely-changing content |
| `/blog`, `/blog/:slug` | Static (public, DB-driven, parameterized) | Public per-slug content; out of PoC scope (see below) — would need one static page per post at build time |
| `/etkinlik/:id` | Static (public, DB-driven, parameterized) | Same reasoning as blog; thousands of ids, out of PoC scope |
| `/status` | Dynamic | Live scraper run status; prerendering it would show stale data immediately |
| `/abone-onay`, `/abone-iptal` | Dynamic, single-use | Token consumed on load — prerendering/caching this response would be actively wrong (breaks or replays the token action) |
| `/etkinlik-talep`, `/oneri-sikayet` | User-interactive | Forms; no content to prerender, the interaction *is* the page |
| `/admin/*` | User-interactive, authenticated | Behind `ProtectedRoute`; per-user, never public/cacheable |
| `/error/server`, `/redirect`, `*` (404) | Static (trivial) | No data dependency, low priority |

**Cross-cutting:** `/`, `/takvim`, and all five landing pages render
through the same `EventListing` component, which layers client-only,
post-hydration interactivity (search, source/location/tag filters,
favorites via `localStorage`) on top of the server-fetched event list.
This is exactly why prerendering these routes needs a hydration
regression test — the prerendered HTML must still hand off cleanly to a
fully-interactive client app.

## PoC scope

Prerender target for this PoC: `/`, `/takvim`, `/hackathonlar`,
`/bootcamplar`, `/online-etkinlikler`, `/bu-haftaki-etkinlikler`,
`/son-basvurular` — the seven static, DB-driven, non-parameterized routes.
`/blog/:slug` and `/etkinlik/:id` are explicitly **out of scope**: they'd
need per-id static generation (crawl all ids/slugs, one HTML file each),
which is a real scale/build-time question deserving its own decision, not
folded into this PoC.

## Decision

**Tool: a small custom Playwright-based prerender script**
(`frontend/scripts/prerender.mjs`), not `vite-plugin-ssg` or `react-snap`.

- `vite-plugin-ssg` targets Vue's SSG ecosystem; there's no maintained
  equivalent for a plain Vite + React Router + react-query v3 app without
  restructuring the app into that plugin's page/data conventions — too
  invasive for a PoC on top of the existing single-`App.jsx` router.
- `react-snap` (the other option issue #77 didn't name but is the
  established tool for exactly this SPA-prerender use case) is
  effectively unmaintained (no meaningful release since ~2020) and pins
  an old Puppeteer; not something to add to a 2026 codebase.
- A direct Playwright script is ~80 lines, uses an actively maintained,
  Microsoft-backed browser automation library already proven in this
  session, and needs zero changes to routing/data-fetching code: it
  serves the real built app, lets the real client-side fetch + render
  happen in headless Chromium, and snapshots the resulting DOM. That
  snapshot becomes the served HTML for that route; the original bundle
  still hydrates over it exactly as before.

**Output layout:** one `dist/<route>/index.html` per prerendered route
(e.g. `dist/takvim/index.html`), `dist/index.html` unchanged. This needs
**zero nginx changes** — [nginx.conf](../../frontend/nginx.conf)'s existing
`try_files $uri $uri/ /index.html` already serves a directory's
`index.html` when present and falls back to the SPA shell otherwise, which
is exactly the semantics a prerendered-directory layout needs.

**Not wired into the production build/Dockerfile in this PoC.** `npm run
build` (used by [Dockerfile](../../frontend/Dockerfile) and CI's frontend
job) is untouched; prerendering is a separate `npm run prerender` script
run on top of an existing `dist/`. Wiring it into the deploy pipeline is a
follow-up decision — Playwright's Chromium download adds real time/flake
risk to CI and the deploy job, and that tradeoff deserves its own
sign-off, not a side effect of this PoC.

## Hydration: from `createRoot` to `hydrateRoot`

Prerendering alone doesn't fix FCP/LCP if the client then discards the
prerendered DOM. `main.jsx` originally called `ReactDOM.createRoot(...)`
unconditionally, which **replaces** `#root`'s contents rather than
reconciling with them — verified empirically: the prerendered HTML painted
first, then was wiped back to the `LoadingSpinner` state for ~1-2 render
frames while the client refetched, before the real content reappeared.
That flash erases most of the benefit this PoC exists to prove.

Fixed by (`frontend/src/main.jsx`, `frontend/src/utils/queryHydration.js`):

- `ReactDOM.hydrateRoot()` when `#root` already has prerendered content
  (feature-detected via child count at boot), `createRoot()` otherwise.
- react-query's `dehydrate`/`Hydrate`: the app writes its query cache into
  a `<script id="__REACT_QUERY_STATE__">` element whenever queries settle;
  the prerender snapshot naturally captures it; on the next boot,
  `<Hydrate state={...}>` seeds the query cache before first render so
  `isLoading` is already `false` — without this, `hydrateRoot` would still
  hit a first-render mismatch (loading state vs. prerendered content) and
  fall back to a full client remount anyway.

**Two real bugs surfaced by turning on hydration**, independent of this
PoC and now fixed:

- `EventCard.jsx` rendered a `<a>` ("Başvur") nested inside the card's
  outer `<Link>` (also an `<a>`) — invalid HTML
  (`validateDOMNesting: <a> cannot appear as a descendant of <a>`), and
  the actual root cause of the visible flash: the browser's HTML parser
  auto-corrects this nesting differently than React's client tree, so the
  two structures never matched. Changed to a `<button>` with
  `window.open(...)`, same UX (opens in a new tab), valid HTML.
- `ThemeToggle.jsx`'s inline `style` prop hydration-mismatches cosmetically
  (`"color: var(--text-primary);"` vs. `"color:var(--text-primary)"`) —
  not a real bug, an artifact of this PoC's specific technique: snapshotting
  `page.content()` captures the *browser's* serialization of the style
  attribute, which isn't byte-identical to React's own serialization on
  the client. A true `renderToString` SSR wouldn't have this class of
  mismatch. Marked `suppressHydrationWarning` since the value is static.

Also excluded `AnnouncementModal` from the prerender pass
(`?__prerender=1`, checked in `HomePage.jsx`): it reveals itself via a
`setTimeout(1000)`, so its rendered output legitimately differs between
"settled" (what a snapshot taken after the modal's timer fires would show)
and "just mounted" (what the client's first hydration render always starts
from). Any snapshot-based prerender technique needs this same treatment
for every timer/interval-driven piece of UI, since — unlike the query-cache
data handled by `dehydrate`/`Hydrate` above — there's no general mechanism
here for passing arbitrary component state (e.g. a `useState`) from the
prerender pass into the client's first render. A real SSR framework
(Next.js, Remix) solves this class of problem systematically; this
lightweight custom script only solves it for react-query data.

**Third bug found and fixed — root cause of the remaining hydration-recovery
events (React errors #418/#423), and unrelated to prerendering:**
`frontend/public/sw.js`'s `activate` handler called `self.clients.claim()`.
Combined with `main.jsx`'s `skipWaiting`-driven
`window.location.reload()` on `'controllerchange'`, `claim()`ing
immediately fires that event for the page that is *currently loading*, not
just already-open tabs from a previous visit — so **every first-time
visitor to the site got a surprise full-page reload ~1-2s after their
first load**, independent of this PoC (verified: reproduces on the
pre-Faz-3 `createRoot` build too, see Before/after measurement below).
That reload is what looked like "1-2 hydration-recovery events": the page
was genuinely reloading and re-hydrating from scratch. Confirmed via
`framenavigated`/`load` event counts (2 `load` events per visit before the
fix, 1 after) and directly reproducing the reported symptom (typed search
text getting silently wiped mid-session) before the fix and its absence
after. Fixed by removing `clients.claim()`: a new service worker now only
takes control on a client's *next* navigation, matching the standard
guidance for this exact footgun — see the comment left in `sw.js`.

With this fixed, `frontend/tests/hydration.spec.js` no longer needs (and
no longer has) the `waitForHydrationToSettle` workaround from an earlier
draft of this PoC — interactions are reliable immediately after hydration.

## Bundle analysis

`npm run analyze` (new script, `vite.analyze.config.js`) builds with
`rollup-plugin-visualizer` and writes `dist/stats.html` — a gzip-sized
treemap of every chunk. To find the *actual* mandatory-before-paint JS for
`/` (not just eyeball the full build manifest, which lists every route's
chunk regardless of whether `/` needs it), captured real network requests
for a fresh `/` load in headless Chromium:

| Chunk | gzip |
|---|---|
| `vendor` (react, react-dom, react-router-dom) | 53.96 kB |
| `index` (App shell: Header, Footer, AuthContext, ThemeContext, ErrorBoundary) | 28.31 kB → **27.43 kB after the trim below** |
| `query` (react-query) | 11.07 kB |
| `ui` (date-fns, react-hot-toast) | 11.22 kB |
| `EventListing` | 2.71 kB |
| `tr` (date-fns Turkish locale) | 2.17 kB |
| `EventCard` | 1.95 kB |
| `HomePage` | 1.40 kB |
| `ShareButtons` | 1.49 kB |
| `TagBadge` | 0.72 kB |
| `ErrorMessage` | 0.35 kB |

`vendor` and `query` are fixed costs of the chosen libraries — not
addressable without a larger migration (e.g. off react-query v3), out of
scope here. `date-fns` usage was already checked and is fully tree-shaken
(every call site does `import { format } from 'date-fns'`, no bloat there).

**Trim made:** `Header.jsx` statically imported `SupportModal` even though
it only renders `if (!show) return null` until a user clicks "Destek Ol" —
shipping it unconditionally in the initial bundle for every visitor.
Changed to `React.lazy()`, only rendered (and only then fetched) once
`showSupport` is true. Verified via network capture: `SupportModal-*.js`
is no longer requested on initial `/` load, is requested on click, and the
modal still opens correctly. Saves ~0.9 kB gzip off the mandatory path —
modest, but it's real, verified, and the same pattern likely applies to
other rarely-opened modals/panels not audited here (out of this PoC's time-box).

## Before/after measurement

**Methodology note:** the Lighthouse CLI hangs (`PAGE_HUNG`) in this
sandbox even completely unthrottled — an environment issue, not something
about the app. Measured the same underlying signals directly instead:
`frontend/scripts/measure.mjs`, a Playwright script driving headless
Chromium via CDP (`Network.emulateNetworkConditions`,
`Emulation.setCPUThrottlingRate`) for throttling. Network/CPU profile
approximates issue #77's original "Slow 4G" methodology (400ms RTT,
~400kbps, 4x CPU throttle), but this is a **same-machine, same-conditions,
before/after comparison to isolate this PoC's effect** — not a
reproduction of issue #77's absolute production numbers (those were
measured against the live deployed site over real infrastructure; this is
client+server both on localhost).

**Before** = this repo at HEAD (pre-Faz-3: CSR only, `createRoot`, no
prerendering) built and served via a bare `vite preview` (git worktree,
same commit CI would build from). **After** = current working tree, built
+ `npm run prerender`'d, served the same way. Both hit the same real
backend/DB. 3 runs each; low variance (medians shown).

**A real methodology trap, found while building this measurement, is worth
naming explicitly:** the obvious approach — `page.goto(url, { waitUntil:
"load" })`, then read native FCP/LCP — silently compares two different
amounts of work. This app's route chunks (`HomePage`, `EventListing`,
`EventCard`, ...) are `React.lazy()`-loaded. The plain-CSR **before**
build's `load` event fires once the tiny app-shell bundle is up — it does
**not** wait for those lazy chunks, so `load` (and anything gated on it)
fires "early" over an almost-empty page. The prerendered **after** build's
initial HTML already *is* the real page, so the browser's preload scanner
discovers and fetches every chunk/image immediately, and `load` honestly
waits for all of it. Naively comparing `load`-gated metrics between the
two made the prerendered build look catastrophically worse (throttled FCP
2.2s vs 0.6s, native LCP 8.7s vs 0.6s) — not because it was worse, but
because it was being honest about finishing real work that the baseline's
`load` event doesn't even count. The fair metric is wall-clock time until
real content (`.event-card`) is actually in the DOM — independent of which
build's `load` event fires early — which is also exactly what issue #77
itself diagnosed as the problem ("element render delay").

| Metric (throttled) | Before | After (initial) | After (optimized) |
|---|---|---|---|
| **Time to real content visible** | **~5.8s** | ~0.7s | **~0.7s (-88%)** |
| First Contentful Paint (native) | ~0.6s | ~2.2s* | ~2.2s* |
| CLS | 0.155 | 0.336 | **0.186** |
| TBT (approx.) | ~22ms | ~380ms | ~300ms (open) |
| Requests / bytes transferred (to `load`) | 192 / 385 KB | 32 / 342 KB | 32 / 351 KB |

\* **FCP caveat, not resolved within this PoC:** native `first-contentful-paint`
fires *later* than real content appears in the "after" build (2.2s vs the
0.7s the content itself takes) — logically backwards, since FCP should
fire at-or-before any specific element's render. Suspected cause: Chromium
may defer the FCP performance-entry timestamp behind compositor frames
delayed by the 4x CPU throttle applied to hydration's own reconciliation
work, but this wasn't confirmed. Flagging rather than hiding it.

**What this actually shows:** the core promise holds and is large — a
real visitor sees real event listings in ~0.7s instead of ~5.8s under
throttled mobile conditions, which is the exact problem issue #77 set out
to fix. That gap was verified three independent ways (direct DOM sampling,
an ad-hoc `waitForSelector` probe, and this script), so it's trustworthy.

**CLS root-caused and improved; the fix is a real bug, not a workaround.**
Instrumented `layout-shift` entries with their source nodes: ~90% of the
CLS score (0.303 of 0.336) came from `<footer>`. Direct measurement of its
`getBoundingClientRect()` over time showed its height jumping 880px →
1017px → 522px → 548px — while the number of `<li>` items inside it never
changed. This rules out "sources data arriving late" (the obvious guess)
and points at the real cause: `index.html`'s Bootstrap/FontAwesome/Google
Fonts CSS loads asynchronously (`rel="preload"` + swap-on-load, an earlier
PageSpeed fix for render-blocking CSS). Before that CSS arrives, Bootstrap's
grid classes (`row`, `col-lg-4`, ...) have no effect, so the footer's
columns stack full-width (tall); once it arrives, they lay out side-by-side
(short) — a large, real reflow. **This is a pre-existing, site-wide
characteristic of the async-CSS-loading pattern, not something this PoC
introduced** — prerendering just makes it *visible*, because real content
is on screen for the whole loading window instead of hidden behind a blank
shell/spinner. No fix was made for this specific mechanism: the two real
options are (a) load Bootstrap synchronously/bundled, which reintroduces
the render-blocking-CSS regression that preload+swap was originally added
to fix, or (b) reserve layout space per-component to absorb the reflow,
which needs a real height estimate and would have to be applied broadly
(the same async-CSS mechanism can affect any Bootstrap-grid-dependent
component, not just Footer) — both are judgment calls beyond this PoC's
scope, not something to guess at with one CSS tweak.

**Separately, found and fixed a real, scoped TBT contributor:**
`watchAndEmbedQueryState()` (`frontend/src/utils/queryHydration.js`)
stayed subscribed to the query cache for the entire session, re-serializing
the *whole* cache to JSON and writing it to the DOM on every later cache
event (filter changes, refetches, ...) — even though the embedded state is
only ever read once, at boot. Nothing after that first read consumes it.
Changed it to unsubscribe after the first fully-settled write. This
measurably improved CLS too (0.336 → 0.186) — plausibly by reducing
main-thread contention during the same window Bootstrap's CSS is
reflowing the page — but did **not** meaningfully move TBT (~380ms →
~300ms). TBT's remaining cost is most likely just the aggregate JS
parse/execute/hydrate time under 4x CPU throttle across all the chunks
this route loads, which isn't something a single scoped code change
fixes — it needs real profiling (React DevTools Profiler flame graph, not
more guessing) to find the next concrete target.

**Recommendation:** the time-to-content win is real, large, and durable —
worth pursuing. CLS is now understood and meaningfully improved, with a
clear, honest explanation for why the remaining piece wasn't fixed here.
TBT remains open and needs a profiling session, not another guess, before
a production rollout decision.

## Consequences

- **Open follow-up before production rollout:** CLS root-caused (async
  Bootstrap CSS reflowing the footer's grid layout — pre-existing,
  site-wide, not introduced by this PoC) and partly improved (0.336 →
  0.186) via an unrelated real fix (`watchAndEmbedQueryState` no longer
  stays subscribed all session); the CSS-reflow mechanism itself is
  unfixed, deliberately, pending a decision between bundling Bootstrap
  synchronously (reintroduces a render-blocking-CSS regression) or
  per-component space reservation (broad, needs real estimates). TBT
  (~22ms → ~300ms) remains open and needs profiling, not another guess.
  See "Before/after measurement." Time-to-content is a large, verified
  win; these are what stand between this PoC and a rollout decision.
- Content freshness for prerendered routes is bound to whenever
  `npm run prerender` last ran, not to page-request time. Acceptable per
  issue #77's own framing (personalization-free pages), but means: if this
  moves to production, prerendering needs to run on every deploy (or on a
  schedule) or event listings will visibly lag the live DB.
- `/blog/:slug` and `/etkinlik/:id` remain client-rendered; their FCP/LCP
  are unaffected by this PoC.
- The hydration regression test (`frontend/tests/hydration.spec.js`)
  covers filter/search/favorite interactions on a prerendered page against
  a mocked API — it is the safety net for "prerendered HTML boots into a
  fully working app," not a substitute for the app's existing (currently
  nonexistent) frontend test suite.
- New devDependencies: `@playwright/test` (prerender + hydration tests),
  `rollup-plugin-visualizer` (bundle analysis). Both dev-only — zero
  runtime bundle impact. Playwright pulls a Chromium binary at
  `npx playwright install`; this is why it's kept out of the default
  `npm ci && npm run build` CI path added in Faz 1.
