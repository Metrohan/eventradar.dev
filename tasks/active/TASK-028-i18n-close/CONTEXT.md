# Generated Continuation Context

Generated at: 2026-08-03T22:04:17+03:00

## Repository

Root: /home/meto/Desktop/Projects/personal/eventradar.dev
Branch: feat/i18n-foundation

## Git status
```text
 M CLAUDE.md
 M frontend/package-lock.json
 M scripts/convert_images.sh
 M scripts/verify_deploy.sh
?? .claude/
?? .coverage
?? .githooks/
?? .github/copilot-instructions.md
?? .meto-ai/
?? AGENTS.md
?? docs/CURRENT_STATE.md
?? docs/DECISIONS.md
?? docs/TROUBLESHOOTING.md
?? justfile
?? scripts/create-handoff-context.sh
?? scripts/create-task.sh
?? tasks/active/TASK-028-i18n-close/CONTEXT.md
```

## Recent commits
```text
570f04a feat(ui): add channel discovery banner and Telegram footer link
7aa75f8 test(analytics): add edge case coverage for get_stats
f075bd1 fix(a11y): make coffee icon decorative in SupportModal
4422b38 fix(auth): change login error detail to Turkish
1f4961f fix(i18n): externalize ThemeToggle title strings and add aria-label
ea17b99 fix(i18n): give ErrorBoundary its own reload/backHome keys
d28dc3e feat(i18n): migrate remaining shared components to use t()
4dd3994 fix(i18n): address Batch 8 review findings
b886fc2 feat(i18n): migrate StatusPage, subscribe/unsubscribe, and error pages to use t()
e33fbf9 fix(i18n): address Batch 7 review findings
```

## Diff summary
```text
 CLAUDE.md                  | 12 ++++++++++++
 frontend/package-lock.json |  3 +++
 scripts/convert_images.sh  |  0
 scripts/verify_deploy.sh   |  0
 4 files changed, 15 insertions(+)
```

## TASK.md

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

## PLAN.md

# PLAN — TASK-028-i18n-close

## Mevcut Davranış

`frontend/src/components/ThemeToggle.jsx` şu anda:

```jsx
title={theme === 'dark' ? "Açık Mod'a Geç" : "Koyu Mod'a Geç"}
```

- `title` attribute'u hardcoded Türkçe string içeriyor.
- `aria-label` attribute'u hiç yok — erişilebilirlik sorunu.
- `useTranslation()` import'u yok.
- `QualityPage.jsx` ve `AdminDashboard.jsx` dosyaları da `t()` kullanmıyor, ama bunlar admin-only sayfa olduğundan public i18n kapsamı dışında.

---

## Doğrulanmış Kök Neden

`ThemeToggle.jsx` bileşeni, issue #28'in ilk commit'inde (`727ffef`) i18n altyapısı kurulurken gözden kaçmış. Kalan tüm public bileşenler `Batch 1-8` migration commit'leri içinde güncellendi (son commit: `ea17b99`). ThemeToggle bu batch'lerin dışında kaldı.

_Kanıt:_ `git log main..HEAD --oneline | grep ThemeToggle` → çıktı yok.

---

## Hedef Davranış

`ThemeToggle.jsx` şunları içerecek:

```jsx
const { t } = useTranslation()
// ...
title={theme === 'dark' ? t('themeToggle.toLightMode') : t('themeToggle.toDarkMode')}
aria-label={theme === 'dark' ? t('themeToggle.toLightMode') : t('themeToggle.toDarkMode')}
```

Dil EN iken tooltip "Switch to Light Mode", TR iken "Açık Mod'a Geç" görünecek. Dil değiştiğinde tooltip reactif olarak güncellenecek.

---

## Etkilenecek Dosyalar

| Dosya | Değişiklik Türü |
|---|---|
| `frontend/src/components/ThemeToggle.jsx` | `useTranslation` ekle, `title` ve `aria-label` i18n key'lerine taşı |
| `frontend/src/i18n/locales/tr/common.json` | `themeToggle` section ekle |
| `frontend/src/i18n/locales/en/common.json` | `themeToggle` section ekle |

Toplam: 3 dosya, minimal diff.

---

## Değerlendirilen Alternatifler

**A) `title` ve `aria-label` için ayrı key'ler kullan**
- Artı: Semantik esneklik
- Eksi: Gereği yok; tooltip ve aria aynı metni taşımalı
- **Karar: Reddedildi**

**B) Sadece `aria-label` ekle, `title`'ı hardcoded bırak**
- Artı: Daha az değişiklik
- Eksi: Issue #28 kriterleri karşılanmaz; "All strings externalized" şartını ihlal eder
- **Karar: Reddedildi**

**C) Her ikisini aynı key'den besle** ← seçilen
- `t('themeToggle.toLightMode')` hem `title` hem `aria-label`'a gider
- Artı: Tek kaynak, senkron kalar, minimal değişim
- **Karar: Kabul edildi**

---

## Veri Bütünlüğü ve Concurrency Riskleri

Yok — bu tamamen client-side string değişikliği. DB, API veya state yok.

---

## Regression Riskleri

| Risk | Olasılık | Önlem |
|---|---|---|
| `suppressHydrationWarning` kaldırılırsa hydration mismatch | Düşük | Bırakılacak |
| TR key'i yanlış yazılırsa fallback TR hardcoded string yerine key görünür | Düşük | JSON doğrulaması ile önlenecek |
| `useTranslation()` hook'u yanlış import edilirse component crash | Çok düşük | Mevcut bileşenlerle aynı import pattern kullanılacak |

---

## Test Matrisi

| Test | Yöntem | Otomasyon |
|---|---|---|
| TR modunda tooltip "Açık Mod'a Geç" görünür | Manuel: browser hover | - |
| EN modunda tooltip "Switch to Light Mode" görünür | Manuel: dil değiştir, hover | - |
| aria-label attribute DOM'da mevcut | Manuel: DevTools inspect | - |
| Dil değişiminde tooltip güncellenir | Manuel: dil toggle, hover | - |
| React hydration hatası yok (console temiz) | Manuel: console kontrol | - |
| JSON dosyaları valid syntax | `python3 -c "import json; json.load(open(...))"` | Evet |

---

## Uygulama Sırası

1. `tr/common.json` → `themeToggle` section ekle (sona, alfabetik değil — mevcut pattern tutarlılığı)
2. `en/common.json` → aynı şekilde
3. `ThemeToggle.jsx` → `useTranslation` import ekle, `title` ve `aria-label` güncelle
4. JSON syntax doğrula
5. Diff'i gözden geçir

---

## Doğrulanmış Gerçekler

- `useTranslation` hook'u ve `t()` fonksiyonu projeye zaten entegre (`react-i18next` yüklü).
- `tr/common.json` ve `en/common.json` dosyaları mevcut ve geçerli JSON.
- `Header.jsx` satır 79: `<LanguageToggle />` render edilmiş — dil değiştirme çalışıyor.
- `LanguageToggle.jsx` aynı `suppressHydrationWarning` pattern'ını kullanıyor — emsal var.
- ThemeToggle, herhangi bir Batch commit'inde güncellenmemiş (git log ile doğrulandı).

---

## Varsayımlar

- Admin sayfaları (`QualityPage.jsx`, `AdminDashboard.jsx`) public i18n scope'u dışında → **Varsayım; onay bekleniyor.**
- `themeToggle` key'i için LanguageToggle'ın kullandığı `header` ya da `nav` section'ına değil, bağımsız bir section'a konulması daha temiz → **Mimari tercih; makul.**

---

## Açık Sorular

1. Admin sayfaları (`QualityPage`, `AdminDashboard`) i18n kapsamında mı? Eğer öyleyse ayrı task olarak ele alınmalı.
2. Bu değişiklikler mevcut branch'te mi yapılacak yoksa ayrı bir commit mi?

---

## Sonraki Issue

#28 kapandıktan sonra sıradaki issue önerisi: **#42** (Login error Turkish) — backend, 2 dosya, çok kısa.

## STATE.yaml

task_id: TASK-028-i18n-close
issues:
  - github: 28
    title: "Multi-language UI (TR / EN)"
  - github: 34
    title: "Add aria-label to theme toggle button"
branch: feat/i18n-foundation
status: implementation_complete
phase: review
created: 2026-08-03

roles:
  architect: claude (current session)
  implementer: pending_human_approval
  reviewer: pending

progress:
  plan_written: true
  human_plan_approved: true
  implementation_started: true
  tests_run: false
  review_done: false
  merged: false

files_to_change:
  - frontend/src/components/ThemeToggle.jsx
  - frontend/src/i18n/locales/tr/common.json
  - frontend/src/i18n/locales/en/common.json

remaining_open_questions:
  - Are admin pages (QualityPage, AdminDashboard) in scope for i18n?

## HANDOFF.md

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

## TESTS.md

# TESTS — TASK-028-i18n-close

## Otomasyon

```bash
# JSON geçerliliği
python3 -c "import json; json.load(open('frontend/src/i18n/locales/tr/common.json'))" && echo "TR OK"
python3 -c "import json; json.load(open('frontend/src/i18n/locales/en/common.json'))" && echo "EN OK"
```

## Manuel Testler (implementasyon sonrası)

| # | Adım | Beklenen Sonuç | Durum |
|---|---|---|---|
| 1 | TR dilinde ThemeToggle üzerine hover | Tooltip: "Açık Mod'a Geç" (dark modda) / "Koyu Mod'a Geç" (light modda) | ⬜ |
| 2 | EN'e geç, hover | Tooltip: "Switch to Light Mode" / "Switch to Dark Mode" | ⬜ |
| 3 | DevTools > Elements > ThemeToggle button | `aria-label` attribute görünmeli | ⬜ |
| 4 | Dil değiştir → tooltip reactif güncellenir | Hover sonrası yeni dil metni | ⬜ |
| 5 | Browser console | i18n missing key uyarısı yok | ⬜ |

## Henüz Çalıştırılmayan Testler

- Unit test (bileşen için test dosyası mevcut değil)
- E2E (Playwright konfigürasyonu mevcut değil)

## REVIEW.md

# REVIEW — TASK-028-i18n-close

Status: **Pending implementation**

Bu dosya implementasyon tamamlandıktan sonra bağımsız reviewer tarafından doldurulacak.

## Checklist (implementasyon sonrası)

- [ ] ThemeToggle.jsx `title` hardcoded string içermiyor
- [ ] ThemeToggle.jsx `aria-label` mevcut ve i18n key'inden besleniyor
- [ ] `tr/common.json` `themeToggle` section geçerli JSON ve doğru string değerleri içeriyor
- [ ] `en/common.json` `themeToggle` section geçerli JSON ve İngilizce string değerleri içeriyor
- [ ] `suppressHydrationWarning` kaldırılmamış
- [ ] Başka dosyalara scope dışı değişiklik yapılmamış

