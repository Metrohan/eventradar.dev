import { useTranslation } from 'react-i18next'
import { tr, enUS } from 'date-fns/locale'

// date-fns locale objects don't come from i18next — every call site that
// formats a date needs to pick the right one based on the active UI
// language, or dates stay Turkish-formatted even in English UI (a real
// bug, not cosmetic, given how central dates are to this app's content).
const LOCALES = { tr, en: enUS }

export const useDateLocale = () => {
  const { i18n } = useTranslation()
  return LOCALES[i18n.language] || tr
}
