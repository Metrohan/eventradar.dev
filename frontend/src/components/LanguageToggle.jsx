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
    >
      {isTurkish ? 'EN' : 'TR'}
    </button>
  )
}

export default LanguageToggle
