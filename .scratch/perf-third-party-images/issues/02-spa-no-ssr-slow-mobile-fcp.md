# Mobile FCP/LCP stuck around 5s: no SSR, blank until JS boots

Status: needs-triage
GitHub: https://github.com/Metrohan/eventradar.dev/issues/77

## Context

After fixing render-blocking CDN CSS and the CLS regressions (see issue 01
and the `fix/google-search-console` PR), a fresh mobile PageSpeed run
(Moto G Power, Slow 4G, 2026-07-17 13:35) still scores Performance 52:

- FCP 4.9s, LCP 5.0s, TBT 0ms, CLS 0.364, SI 4.9s
- LCP breakdown: TTFB 0ms, **"Öğe oluşturma gecikmesi" (element render
  delay) 2700ms** — i.e. almost the entire LCP time is spent *after*
  resources finish loading, waiting for something to actually paint.
- The render-blocking-CSS audit is now down to just our own bundled
  `index-*.css` (~120ms estimated savings) — the Bootstrap/FontAwesome/
  Google Fonts preload+swap fix from the earlier round worked as intended.

## Root cause

`frontend/` is a client-rendered SPA (Vite + React, `ReactDOM.createRoot`
in `main.jsx`, no SSR/prerendering). Under throttled mobile networks,
nothing paints until: HTML → JS bundle downloads → parses → executes →
React mounts. CSS optimization can't fix this because the bottleneck has
moved to JS boot time, not stylesheet blocking.

## Why this is a separate issue

Fixing this properly means one of:
1. Server-side rendering or static prerendering for at least the initial
   HTML shell (e.g. Vite SSR, or a prerendering step for the
   landing/listing pages that dominate organic traffic).
2. Reducing the JS payload needed before first paint (the `vendor-*.js`
   chunk is 163KB / 54KB gzipped) via further code-splitting.

Both are meaningfully larger changes than the markup/nginx/CSS fixes
already shipped — they touch the build pipeline and possibly hosting
(SSR needs a Node runtime, not just static files behind nginx). Out of
scope for incremental PageSpeed patches.

## Suggested approach (not decided)

- Start with a scoped prerendering pass (e.g. `vite-plugin-ssg` or a
  simple build-time render of `/`, `/takvim`, `/hackathonlar`, etc. — the
  pages in `frontend/public/sitemap.xml` — into static HTML) rather than
  full SSR, since these pages don't need per-request personalization.
- Re-measure FCP/LCP against the *current* baseline (this issue) after
  any change, not the original pre-fix numbers, to isolate the effect.

## Acceptance criteria

- [ ] Mobile FCP/LCP measurably improve without regressing CLS/TBT
- [ ] The homepage still functions correctly for client-side interactions
      (filters, search, favorites) after any prerendering change
