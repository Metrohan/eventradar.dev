function setMeta(name, content, property = false) {
  const attr = property ? `[property="${name}"]` : `[name="${name}"]`
  let el = document.querySelector(`meta${attr}`)
  if (!el) {
    el = document.createElement('meta')
    el.setAttribute(property ? 'property' : 'name', name)
    document.head.appendChild(el)
  }
  el.setAttribute('content', content)
}

/**
 * Statik SEO landing sayfaları (kategori/zaman bazlı etkinlik listeleri) için
 * title/description/canonical/OG etiketlerini ayarlar. EventDetailPage kendi
 * (görsel + JSON-LD içeren) daha zengin versiyonunu kullanmaya devam eder.
 *
 * `title` stays Turkish and drives og:title/twitter:title/description/canonical
 * — these are the route's canonical, crawler-facing identity (see
 * docs/superpowers/specs/2026-08-01-i18n-infrastructure-design.md: routes
 * stay Turkish regardless of UI language). `tabTitle` is what the visitor
 * actually sees constantly (browser tab, bookmarks, history) — a page
 * migrated to i18n should pass a `t()`-translated `tabTitle` so it matches
 * the visible UI language; pages not yet migrated can omit it and get the
 * previous behavior (document.title === title) unchanged.
 */
export function setPageSEO({ title, tabTitle, description, path }) {
  document.title = tabTitle || title
  setMeta('description', description)

  const canonicalUrl = `https://eventradar.dev${path}`
  setMeta('og:title', title, true)
  setMeta('og:description', description, true)
  setMeta('og:url', canonicalUrl, true)
  setMeta('og:type', 'website', true)
  setMeta('twitter:card', 'summary', true)
  setMeta('twitter:title', title)
  setMeta('twitter:description', description)

  let canonical = document.querySelector('link[rel="canonical"]')
  if (!canonical) {
    canonical = document.createElement('link')
    canonical.setAttribute('rel', 'canonical')
    document.head.appendChild(canonical)
  }
  canonical.setAttribute('href', canonicalUrl)
}
