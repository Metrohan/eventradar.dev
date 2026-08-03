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
