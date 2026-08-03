# TASK-028-i18n-close

## Issue
GitHub #28 — Multi-language UI (TR / EN)
GitHub #34 — Add aria-label to theme toggle button (closes together)

## Branch
`feat/i18n-foundation` (already active)

## Observable Problem

`ThemeToggle.jsx` renders a `<button>` whose `title` attribute contains hardcoded Turkish strings
(`"Açık Mod'a Geç"` / `"Koyu Mod'a Geç"`) and has no `aria-label` attribute.
This means:
- Screen-reader users get no accessible label on the theme button.
- English-speaking visitors get Turkish tooltip text regardless of their language preference.
- Issue #28 acceptance criterion "All static UI strings externalized" is not fully met.

All other public-facing pages and components already use `t()` from `react-i18next`.

## Desired Outcome

- `ThemeToggle.jsx` reads its tooltip and aria-label from the i18n translation system.
- Both `tr/common.json` and `en/common.json` contain a `themeToggle` section with the relevant keys.
- Issue #28 acceptance criteria are fully satisfied.
- Issue #34 is closed as a by-product.

## Testable Acceptance Criteria

1. `ThemeToggle.jsx` uses `useTranslation()` and calls `t('themeToggle.toLightMode')` / `t('themeToggle.toDarkMode')`.
2. `ThemeToggle` renders an `aria-label` attribute derived from the same translation key as `title`.
3. `tr/common.json` contains `themeToggle.toLightMode = "Açık Mod'a Geç"` and `themeToggle.toDarkMode = "Koyu Mod'a Geç"`.
4. `en/common.json` contains `themeToggle.toLightMode = "Switch to Light Mode"` and `themeToggle.toDarkMode = "Switch to Dark Mode"`.
5. No raw Turkish/English strings remain inside `ThemeToggle.jsx`.
6. Language switch (EN/TR) updates the tooltip text reactively.

## In Scope

- `frontend/src/components/ThemeToggle.jsx` — add i18n + aria-label
- `frontend/src/i18n/locales/tr/common.json` — add `themeToggle` section
- `frontend/src/i18n/locales/en/common.json` — add `themeToggle` section

## Out of Scope

- `QualityPage.jsx` — admin-only page; public i18n not required
- `AdminDashboard.jsx` — admin-only page; public i18n not required
- Any new translation namespace or i18n library changes
- SEO meta / JSON-LD (already correctly excluded from i18n)
- Backend login error message (separate issue #42)

## Constraints

- Must not change the `suppressHydrationWarning` attribute (prerender PoC compatibility)
- Must not break existing TR behaviour
- `title` and `aria-label` should use the same key so they stay in sync
