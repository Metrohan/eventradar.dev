# REVIEW — TASK-028-i18n-close

Status: **Pending independent review**

Commit to review: **`1f4961f`** — `fix(i18n): externalize ThemeToggle title strings and add aria-label`

İnceleme komutu: `git show 1f4961f`

## Checklist

- [ ] `ThemeToggle.jsx` — `title` attribute artık hardcoded string içermiyor
- [ ] `ThemeToggle.jsx` — `aria-label` attribute mevcut ve i18n key'inden besleniyor
- [ ] `ThemeToggle.jsx` — `useTranslation` import'u doğru (react-i18next'ten)
- [ ] `ThemeToggle.jsx` — `suppressHydrationWarning` attribute kaldırılmamış
- [ ] `tr/common.json` — `themeToggle` section geçerli JSON, doğru Türkçe değerler
- [ ] `en/common.json` — `themeToggle` section geçerli JSON, doğru İngilizce değerler
- [ ] Scope dışı dosyaya dokunulmamış (diff yalnızca 3 dosyayı kapsıyor)

## Bulgular

_(Reviewer dolduracak — BLOCKER / CRITICAL / MAJOR / MINOR / NIT)_

## Karar

- [ ] Onayla — merge'e hazır
- [ ] Bloke — aşağıdaki bulgular giderilmeli
