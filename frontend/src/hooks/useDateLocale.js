import { useTranslation } from 'react-i18next'
import { tr, enUS } from 'date-fns/locale'

// date-fns locale objects don't come from i18next — every call site that
// formats a date needs to pick the right one based on the active UI
// language, or dates stay Turkish-formatted even in English UI (a real
// bug, not cosmetic, given how central dates are to this app's content).
const LOCALES = { tr, en: enUS }

export const useDateLocale = () => {
  const { i18n } = useTranslation()
  // i18n.language is the RAW, un-normalized value from
  // i18next-browser-languagedetector (e.g. 'en-US', 'en-GB' — most real
  // browsers report a regional variant, not bare 'en'). i18next core never
  // normalizes that property. i18n.resolvedLanguage is the language i18next
  // actually resolved translations against (e.g. 'en'), so it's the correct
  // lookup key here — using i18n.language would make LOCALES['en-US'] miss
  // and silently fall back to the Turkish date-fns locale for most English
  // visitors.
  return LOCALES[i18n.resolvedLanguage] || tr
}
