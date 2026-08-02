import React from 'react'
import { useTranslation } from 'react-i18next'

const LanguageToggle = () => {
  const { i18n } = useTranslation()
  const isTurkish = i18n.language === 'tr'

  const toggle = () => {
    i18n.changeLanguage(isTurkish ? 'en' : 'tr')
  }

  return (
    <button
      onClick={toggle}
      className="btn btn-link text-decoration-none p-2"
      title={isTurkish ? 'Switch to English' : "Türkçe'ye geç"}
      style={{ color: 'var(--text-primary)', fontWeight: 700, fontSize: '0.85rem' }}
      // The prerender PoC snapshots the browser-serialized DOM (see
      // docs/adr/0006-prerender-poc.md), which normalizes this inline
      // style string slightly differently than React's own serialization on
      // hydrate. Same values, cosmetic-only diff — suppress rather than let
      // it force a client remount.
      suppressHydrationWarning
    >
      {isTurkish ? 'EN' : 'TR'}
    </button>
  )
}

export default LanguageToggle
