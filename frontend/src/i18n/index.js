import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import LanguageDetector from 'i18next-browser-languagedetector'
import tr from './locales/tr/common.json'
import en from './locales/en/common.json'
import { isPrerendered } from '../utils/queryHydration'

// See "Important: interaction with the prerender PoC" at the top of
// docs/superpowers/plans/2026-08-01-i18n-foundation.md. Prerendered
// snapshots are always captured in Turkish; forcing the same language for
// this module's initial resolution on a prerendered page keeps main.jsx's
// hydrateRoot() first render matching the snapshot. main.jsx applies the
// visitor's real detected/stored language afterward via changeLanguage().
const wasPrerendered = isPrerendered()

// Must be computed BEFORE i18n.init() below. When init() forces
// `lng: 'tr'` on a prerendered page, it triggers a synchronous
// changeLanguage('tr') call, which invokes
// languageDetector.cacheUserLanguage('tr') — and with
// caches: ['localStorage'] configured, that unconditionally overwrites
// localStorage['eventradar:lang'] with 'tr', even though 'tr' came from
// the forced option, not from the visitor's real preference. Reading the
// true stored/navigator value here, ahead of init(), avoids capturing a
// value init() has already clobbered. Used by main.jsx to apply the real
// preference after a forced-tr hydration.
export const detectedLanguage = (() => {
  const stored = localStorage.getItem('eventradar:lang')
  if (stored === 'tr' || stored === 'en') return stored
  const nav = (navigator.language || 'tr').slice(0, 2)
  return nav === 'en' ? 'en' : 'tr'
})()

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      tr: { common: tr },
      en: { common: en },
    },
    ns: ['common'],
    defaultNS: 'common',
    fallbackLng: 'tr',
    lng: wasPrerendered ? 'tr' : undefined,
    detection: {
      order: ['localStorage', 'navigator'],
      lookupLocalStorage: 'eventradar:lang',
      caches: ['localStorage'],
    },
    interpolation: { escapeValue: false },
    // Missing keys: warn in dev so they're caught during the page-migration
    // follow-up plan; in production, i18next's fallbackLng ('tr') already
    // makes a missing 'en' key silently render the Turkish string instead
    // of the raw key.
    saveMissing: import.meta.env.DEV,
    missingKeyHandler: import.meta.env.DEV
      ? (lngs, ns, key) => console.warn(`[i18n] missing key: ${ns}:${key} (${lngs.join(',')})`)
      : undefined,
  })

document.documentElement.lang = wasPrerendered ? 'tr' : detectedLanguage
i18n.on('languageChanged', (lng) => {
  document.documentElement.lang = lng
})

export default i18n
