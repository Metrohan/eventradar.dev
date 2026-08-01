import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider, Hydrate, dehydrate } from 'react-query'
import App from './App.jsx'
import './index.css'
import { readEmbeddedQueryState, isPrerendered, watchAndEmbedQueryState } from './utils/queryHydration'

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
