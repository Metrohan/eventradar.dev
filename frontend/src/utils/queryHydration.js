// Bridges react-query's cache into the prerendered HTML (see
// docs/adr/0006-prerender-poc.md). Without this, the client's first render
// starts from an empty query cache (isLoading: true) while the prerendered
// DOM already shows real event cards — React discards the mismatch and
// re-renders from a loading state, erasing the prerender's FCP/LCP benefit.
//
// readEmbeddedQueryState() runs once at boot, before the app renders, and
// feeds react-query's <Hydrate> so the first render already has the same
// data the prerendered markup was built from.
//
// watchAndEmbedQueryState() runs on every page (prerendered or not) and
// keeps a <script id="__REACT_QUERY_STATE__"> element in sync with the
// cache until the first time every in-flight query has settled, then
// unsubscribes. The embedded state is only ever consumed once — read at
// boot by readEmbeddedQueryState(), or captured by a prerender snapshot —
// so continuing to re-serialize the whole cache on every later cache event
// (filter changes, refetches, ...) for the rest of the session is pure
// main-thread cost with no consumer. Verified this was measurably adding
// to TBT under CPU throttling — see docs/adr/0006-prerender-poc.md.

const STATE_ELEMENT_ID = "__REACT_QUERY_STATE__";

export function readEmbeddedQueryState() {
  if (typeof document === "undefined") return undefined;
  const el = document.getElementById(STATE_ELEMENT_ID);
  if (!el || !el.textContent) return undefined;
  try {
    return JSON.parse(el.textContent);
  } catch {
    return undefined;
  }
}

export function isPrerendered() {
  if (typeof document === "undefined") return false;
  const root = document.getElementById("root");
  return !!root && root.childElementCount > 0;
}

export function watchAndEmbedQueryState(queryClient, dehydrate) {
  let unsubscribe;

  const sync = () => {
    if (queryClient.isFetching() > 0) return;

    let el = document.getElementById(STATE_ELEMENT_ID);
    if (!el) {
      el = document.createElement("script");
      el.type = "application/json";
      el.id = STATE_ELEMENT_ID;
      document.body.appendChild(el);
    }
    el.textContent = JSON.stringify(dehydrate(queryClient));

    // First fully-settled snapshot is the only one anything reads — stop
    // paying to keep it fresh for the rest of the session.
    unsubscribe?.();
  };

  sync();
  if (queryClient.isFetching() > 0) {
    unsubscribe = queryClient.getQueryCache().subscribe(sync);
  }
  return () => unsubscribe?.();
}
