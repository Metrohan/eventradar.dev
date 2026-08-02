import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider, Hydrate, dehydrate } from 'react-query'
import App from './App.jsx'
import './index.css'
import { readEmbeddedQueryState, isPrerendered, watchAndEmbedQueryState } from './utils/queryHydration'
import i18n, { detectedLanguage } from './i18n'

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
})

const root = document.getElementById('root')
const wasPrerendered = isPrerendered()
const dehydratedState = readEmbeddedQueryState()

const app = (
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <Hydrate state={dehydratedState}>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </Hydrate>
    </QueryClientProvider>
  </React.StrictMode>
)

// A prerendered page (see docs/adr/0006-prerender-poc.md) already has real
// markup in #root; hydrateRoot reconciles with it instead of replacing it,
// which is what actually preserves the prerender's FCP/LCP benefit. The
// <Hydrate> above feeds the same query data the prerender was built from,
// so this first render produces matching markup instead of a loading state.
if (wasPrerendered) {
  ReactDOM.hydrateRoot(root, app)
  // frontend/src/i18n/index.js forced the initial language to 'tr' to
  // match the prerendered snapshot. Now that hydration succeeded against
  // that matching markup, apply the visitor's real detected/stored
  // language if different — a normal post-hydration re-render via
  // react-i18next's useTranslation(), not a hydration mismatch.
  if (detectedLanguage !== 'tr') {
    i18n.changeLanguage(detectedLanguage)
  }
} else {
  ReactDOM.createRoot(root).render(app)
}

watchAndEmbedQueryState(queryClient, dehydrate)

if ('serviceWorker' in navigator) {
  let refreshing = false
  navigator.serviceWorker.addEventListener('controllerchange', () => {
    if (refreshing) return
    refreshing = true
    window.location.reload()
  })

  window.addEventListener('load', () => {
    navigator.serviceWorker
      .register('/sw.js')
      .then(registration => registration.update())
      .catch(() => {
        // Service worker kaydı başarısız olsa da uygulama normal şekilde çalışmaya devam eder.
      })
  })
}
