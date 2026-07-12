const CACHE_NAME = 'eventradar-v2'
const PRECACHE_URLS = ['/', '/manifest.json', '/favicon.ico']

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(PRECACHE_URLS))
  )
  self.skipWaiting()
})

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key)))
    )
  )
  self.clients.claim()
})

self.addEventListener('push', (event) => {
  if (!event.data) return
  const payload = event.data.json()
  event.waitUntil(
    self.registration.showNotification(payload.title || 'TechEventRadar', {
      body: payload.body || '',
      icon: '/pwa-icon-192.png',
      badge: '/pwa-icon-192.png',
      data: { url: payload.url || '/' },
    })
  )
})

self.addEventListener('notificationclick', (event) => {
  event.notification.close()
  const url = event.notification.data?.url || '/'
  event.waitUntil(self.clients.openWindow(url))
})

self.addEventListener('fetch', (event) => {
  const { request } = event
  if (request.method !== 'GET') return

  const url = new URL(request.url)

  // API yanıtları her zaman güncel olmalı (etkinlik verisi günlük değişiyor);
  // service worker bunları hiç önbelleğe almaz, doğrudan ağa gider.
  if (url.pathname.startsWith('/api/')) return

  // SPA navigasyonlarında önce ağı kullan. Böylece yeni deploy sonrasında eski
  // index.html ve eski bundle referansları cache'den geri gelmez. Ağ yoksa son
  // başarılı uygulama kabuğuna düş.
  if (request.mode === 'navigate') {
    event.respondWith(
      fetch(request)
        .then((response) => {
          if (response.ok) {
            const clone = response.clone()
            caches.open(CACHE_NAME).then((cache) => cache.put('/', clone))
          }
          return response
        })
        .catch(() => caches.match('/'))
    )
    return
  }

  // Statik varlıklar (JS/CSS/görsel/font): cache-first, ağ yalnızca eksikse.
  event.respondWith(
    caches.match(request).then((cached) => {
      if (cached) return cached
      return fetch(request)
        .then((response) => {
          if (response.ok) {
            const clone = response.clone()
            caches.open(CACHE_NAME).then((cache) => cache.put(request, clone))
          }
          return response
        })
        .catch(() => caches.match('/'))
    })
  )
})
