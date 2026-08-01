#!/usr/bin/env node
// Before/after performance measurement for the prerender PoC
// (see docs/adr/0006-prerender-poc.md "Before/after measurement").
//
// Drives headless Chromium via CDP, throttles network/CPU to approximate
// issue #77's original "Slow 4G" methodology, and reads browser-native
// paint/layout-shift/longtask signals via PerformanceObserver injected
// before navigation. Not a Lighthouse score — Lighthouse's CLI hangs
// (PAGE_HUNG) in this sandbox even fully unthrottled, an environment issue
// unrelated to the app — but the same underlying browser metrics.
//
// Deliberately does NOT report native LargestContentfulPaint: this app's
// route chunks are React.lazy-loaded, and the plain-CSR baseline only
// requests them *after* the `load` event fires while a prerendered build's
// already-rendered markup pulls them in immediately. That makes `load` and
// LCP (which both implicitly depend on how much a browser decided to do
// before/around them) not comparable between the two builds — verified
// empirically, see docs/adr/0006-prerender-poc.md "Before/after
// measurement". `timeToContentMs` (wall clock until `.event-card` is
// actually in the DOM) is the metric that's actually apples-to-apples, and
// matches what issue #77 itself diagnosed ("element render delay").
//
// Usage: node scripts/measure.mjs <url> [--runs 3] [--label after]

import { chromium } from "@playwright/test";

function parseArgs(argv) {
  const url = argv[0];
  if (!url) {
    console.error("Usage: node scripts/measure.mjs <url> [--runs 3] [--label x]");
    process.exit(1);
  }
  const runsIdx = argv.indexOf("--runs");
  const runs = runsIdx !== -1 ? parseInt(argv[runsIdx + 1], 10) : 3;
  const labelIdx = argv.indexOf("--label");
  const label = labelIdx !== -1 ? argv[labelIdx + 1] : url;
  return { url, runs, label };
}

// Approximates issue #77's original mobile PageSpeed run (Moto G Power,
// Slow 4G): ~400ms RTT, ~400kbps down/up, 4x CPU slowdown.
const NETWORK_CONDITIONS = {
  offline: false,
  latency: 400,
  downloadThroughput: (400 * 1024) / 8,
  uploadThroughput: (400 * 1024) / 8,
};
const CPU_THROTTLE_RATE = 4;

const COLLECT_METRICS_SCRIPT = `
window.__perf = { paints: {}, cls: 0, longTaskTotal: 0 };
new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    window.__perf.paints[entry.name] = entry.startTime;
  }
}).observe({ type: "paint", buffered: true });
new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    if (!entry.hadRecentInput) window.__perf.cls += entry.value;
  }
}).observe({ type: "layout-shift", buffered: true });
new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    // TBT approximation: time each long task spends beyond the 50ms budget.
    window.__perf.longTaskTotal += Math.max(0, entry.duration - 50);
  }
}).observe({ type: "longtask", buffered: true });
`;

async function measureOnce(browser, url) {
  const context = await browser.newContext();
  const page = await context.newPage();
  const client = await context.newCDPSession(page);

  await client.send("Network.enable");
  await client.send("Network.emulateNetworkConditions", NETWORK_CONDITIONS);
  await client.send("Emulation.setCPUThrottlingRate", { rate: CPU_THROTTLE_RATE });

  let requestCount = 0;
  let bytesTransferred = 0;
  page.on("requestfinished", async (req) => {
    requestCount += 1;
    try {
      const res = await req.response();
      const headers = res ? await res.allHeaders() : {};
      const len = headers["content-length"];
      if (len) bytesTransferred += parseInt(len, 10);
    } catch {
      // response may already be gone; ignore for this approximate total
    }
  });

  await page.addInitScript(COLLECT_METRICS_SCRIPT);

  const navStart = Date.now();
  // Deliberately not `waitUntil: "load"`: this app lazy-loads route chunks
  // (React.lazy) that this repo's plain-CSR baseline only requests *after*
  // `load` fires, while the prerendered build's already-rendered markup
  // pulls them in immediately — the two builds' `load` events end up
  // measuring different amounts of real work, not a fair comparison. The
  // metric that's actually comparable, and matches what issue #77 diagnosed
  // ("element render delay"), is wall-clock time until real event content
  // is visible.
  page.goto(url, { timeout: 60000 }).catch(() => {});
  await page.waitForSelector(".event-card", { timeout: 60000 });
  const timeToContentMs = Date.now() - navStart;

  // Let the rest of the page (images, fonts, remaining chunks) finish so
  // request/byte counts and CLS/longtask/FCP observers reflect the full
  // page, not just what's arrived by the moment content first appears.
  await page.waitForLoadState("load").catch(() => {});
  await page.waitForTimeout(1000);

  const perf = await page.evaluate(() => window.__perf);
  await context.close();

  return {
    fcp: perf.paints["first-contentful-paint"] ?? null,
    timeToContentMs,
    cls: perf.cls,
    tbtApprox: perf.longTaskTotal,
    requestCount,
    bytesTransferred,
  };
}

function median(nums) {
  const sorted = [...nums].sort((a, b) => a - b);
  const mid = Math.floor(sorted.length / 2);
  return sorted.length % 2 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2;
}

async function main() {
  const { url, runs, label } = parseArgs(process.argv.slice(2));
  const executablePath = process.env.PRERENDER_CHROMIUM_PATH || undefined;
  const browser = await chromium.launch({ executablePath });

  const samples = [];
  for (let i = 0; i < runs; i++) {
    const result = await measureOnce(browser, url);
    samples.push(result);
    console.error(`[${label}] run ${i + 1}/${runs}:`, JSON.stringify(result));
  }
  await browser.close();

  const summary = {
    label,
    url,
    runs,
    fcpMs: median(samples.map((s) => s.fcp).filter((v) => v != null)),
    timeToContentMs: median(samples.map((s) => s.timeToContentMs)),
    cls: median(samples.map((s) => s.cls)),
    tbtApproxMs: median(samples.map((s) => s.tbtApprox)),
    requestCount: median(samples.map((s) => s.requestCount)),
    bytesTransferred: median(samples.map((s) => s.bytesTransferred)),
  };
  console.log(JSON.stringify(summary, null, 2));
}

main().catch((err) => {
  console.error(err);
  process.exitCode = 1;
});
