# HANDOFF — TASK-028-i18n-close

## Durum: Plan hazır, insan onayı bekleniyor

## Ne Yapıldı (Bu Oturum)

- GitHub issue #28 ve #34 analiz edildi.
- `feat/i18n-foundation` branch'indeki mevcut i18n durumu incelendi.
- 13 commit'in hangi bileşenleri kapsadığı doğrulandı.
- ThemeToggle.jsx'in tek kalan eksik olduğu tespit edildi.
- TASK.md, PLAN.md, STATE.yaml, HANDOFF.md oluşturuldu.

## Mevcut Durum

Issue #28 acceptance criteria durumu:
- ✅ i18n library integrated (react-i18next)
- ✅ Language switcher in header (LanguageToggle.jsx, Header.jsx:79)
- ✅ Language preference persisted in localStorage (`eventradar:lang`)
- ⚠️ All static UI strings externalized → **ThemeToggle.jsx `title` hâlâ hardcoded**

## Bir Sonraki Kesin İşlem

**İnsan planı onayladıktan sonra** implementer şunu yapacak:

### Adım 1 — `tr/common.json`'a ekle (dosyanın sonuna, `supportModal`'dan sonra)

```json
"themeToggle": {
  "toLightMode": "Açık Mod'a Geç",
  "toDarkMode": "Koyu Mod'a Geç"
}
```

### Adım 2 — `en/common.json`'a aynı şekilde ekle

```json
"themeToggle": {
  "toLightMode": "Switch to Light Mode",
  "toDarkMode": "Switch to Dark Mode"
}
```

### Adım 3 — `ThemeToggle.jsx`'i güncelle

```jsx
import { useTranslation } from 'react-i18next'
// ...
const { t } = useTranslation()
const label = theme === 'dark' ? t('themeToggle.toLightMode') : t('themeToggle.toDarkMode')
// button'da:
title={label}
aria-label={label}
```

### Adım 4 — Doğrula

```bash
python3 -c "import json; json.load(open('frontend/src/i18n/locales/en/common.json'))" && echo "OK"
python3 -c "import json; json.load(open('frontend/src/i18n/locales/tr/common.json'))" && echo "OK"
```

## Bağımlılıklar / Riskler

- Sıfır — saf string değişikliği, runtime bağımlılığı yok.
- `suppressHydrationWarning` bırakılacak.

## Açık Soru (Onay Gerekiyor)

Admin sayfaları (`QualityPage.jsx`, `AdminDashboard.jsx`) scope'a giriyor mu?
- Eğer hayır → #28 bu task ile kapanır.
- Eğer evet → ayrı task açılacak.
