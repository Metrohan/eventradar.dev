#!/usr/bin/env node
// Build-time prerender PoC (see docs/adr/0006-prerender-poc.md).
//
// Serves an already-built dist/ via `vite preview`, visits each target
// route in headless Chromium, waits for the real client-side data fetch
// + render to finish (same code path a real visitor hits), and snapshots
// the resulting DOM as dist/<route>/index.html. The original dist/index.html
// is left untouched, so every other route still falls back to the normal
// client-rendered SPA shell via nginx's `try_files ... /index.html`.
//
// Usage: node scripts/prerender.mjs [--base-url http://127.0.0.1:4173]

import { chromium } from "@playwright/test";
import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DIST_DIR = path.resolve(__dirname, "..", "dist");

// PoC scope per ADR-0006: static, DB-driven, non-parameterized routes only.
const ROUTES = [
  "/",
  "/takvim",
  "/hackathonlar",
  "/bootcamplar",
  "/online-etkinlikler",
  "/bu-haftaki-etkinlikler",
  "/son-basvurular",
];

const LOADING_SELECTOR = ".loading-spinner";
const LOAD_TIMEOUT_MS = 15000;

function parseBaseUrl(argv) {
  const idx = argv.indexOf("--base-url");
  if (idx !== -1 && argv[idx + 1]) return argv[idx + 1];
  return "http://127.0.0.1:4173";
}

// index.html loads Google Fonts/Bootstrap/FontAwesome CSS off the critical
// path via rel="preload" + onload="this.onload=null;this.rel='stylesheet'"
// (see index.html's own comment). By the time we snapshot page.content(),
// that onload has already fired in the live browser session, so the *live
// DOM* now shows rel="stylesheet" on those tags — a real, correct
// description of that session, but wrong to freeze into a static file: a
// fresh visitor loading the snapshot verbatim would get three
// render-blocking external stylesheets instead of the async-loaded ones,
// silently reintroducing the exact render-blocking-CSS problem the
// preload pattern exists to avoid. Undo the mutation before saving.
function restoreAsyncStylesheetLinks(html) {
  return html.replace(
    /<link rel="stylesheet" as="style"([^>]*onload="this\.onload=null;this\.rel='stylesheet'"[^>]*)>/g,
    `<link rel="preload" as="style"$1>`,
  );
}

async function withRetry(fn, attempts = 3, delayMs = 300) {
  let lastErr;
  for (let i = 0; i < attempts; i++) {
    try {
      return await fn();
    } catch (err) {
      lastErr = err;
      await new Promise((resolve) => setTimeout(resolve, delayMs));
    }
  }
  throw lastErr;
}

async function prerenderRoute(browser, baseUrl, route) {
  const page = await browser.newPage();
  try {
    // ?__prerender=1 tells HomePage to skip the timer-driven AnnouncementModal
    // reveal, so the snapshot matches the state the client's first hydration
    // render starts from (see docs/adr/0006-prerender-poc.md). The query
    // string is only used to drive this navigation — it isn't part of the
    // saved dist/<route>/index.html file.
    const separator = route.includes("?") ? "&" : "?";
    const url = `${baseUrl}${route}${separator}__prerender=1`;

    // Deliberately not `networkidle`: this app has background activity
    // (service worker registration, react-query, analytics) that can keep
    // the network non-idle well past when the page is actually usable.
    await page.goto(url, { waitUntil: "load" });

    // React mounts asynchronously (lazy-loaded route chunk); wait for the
    // root to actually have content before checking for a loading spinner,
    // otherwise an empty #root reads as "no spinner" and we'd capture the
    // page before it ever rendered.
    await page.waitForFunction(
      () => (document.getElementById("root")?.childElementCount ?? 0) > 0,
      { timeout: LOAD_TIMEOUT_MS },
    );

    const spinner = page.locator(LOADING_SELECTOR).first();
    if (await spinner.count()) {
      await spinner.waitFor({ state: "detached", timeout: LOAD_TIMEOUT_MS });
    }

    // Give in-flight re-renders (e.g. a second query resolving right after
    // the spinner clears) a moment to settle before snapshotting.
    await page.waitForTimeout(300);
    const html = restoreAsyncStylesheetLinks(await withRetry(() => page.content()));
    const outDir =
      route === "/" ? DIST_DIR : path.join(DIST_DIR, route.replace(/^\//, ""));
    await mkdir(outDir, { recursive: true });
    await writeFile(path.join(outDir, "index.html"), html, "utf-8");

    const bytes = Buffer.byteLength(html, "utf-8");
    console.log(`prerendered ${route} -> ${path.relative(DIST_DIR, outDir)}/index.html (${bytes} bytes)`);
  } finally {
    await page.close();
  }
}

async function main() {
  const baseUrl = parseBaseUrl(process.argv.slice(2));
  const executablePath = process.env.PRERENDER_CHROMIUM_PATH || undefined;
  const browser = await chromium.launch({ executablePath });

  try {
    for (const route of ROUTES) {
      await prerenderRoute(browser, baseUrl, route);
    }
  } finally {
    await browser.close();
  }
}

main().catch((err) => {
  console.error(err);
  process.exitCode = 1;
});
