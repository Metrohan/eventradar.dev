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
 */
export function setPageSEO({ title, description, path }) {
  document.title = title
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
