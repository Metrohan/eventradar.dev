# Frontend Pages Redesign — Spec

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Redesign FreeTrainingsPage, SuggestionPage, and EventRequestPage to match the dark glassmorphism design language of the existing HomePage.

**Architecture:** Pure frontend changes — no backend or API modifications. All three pages are in `frontend/src/pages/`. Styles follow the existing CSS custom properties in `frontend/src/index.css`.

**Tech Stack:** React, CSS custom properties (`var(--bg-primary)`, `var(--action-primary)`, etc.), existing `index.css` conventions, react-hook-form, react-query.

---

## Design Language Reference

Follow these patterns from the existing codebase:

- **Cards:** `background: var(--bg-card)`, `border: 1px solid var(--border-color)`, `border-radius: 12-16px`
- **Gradient buttons:** `background: linear-gradient(135deg, #38bdf8, #6366f1)`, white text, `border: none`
- **Gradient headings:** inline style with `background: linear-gradient(135deg, #38bdf8, #6366f1); -webkit-background-clip: text; -webkit-text-fill-color: transparent`
- **Muted text:** `color: var(--text-muted)`
- **Input fields:** `background: rgba(255,255,255,0.04)`, `border: 1px solid rgba(255,255,255,0.1)`, `border-radius: 8px`, focus border `rgba(56,189,248,0.5)`
- **Category badges:** same style as `TagBadge.jsx` — colored background with matching border and text

---

## Page 1: FreeTrainingsPage (`frontend/src/pages/FreeTrainingsPage.jsx`)

### Layout
- Hero section: gradient title + subtitle
- Filter row: search input + category badge filters
- Responsive grid: 3 columns on desktop, 2 on tablet, 1 on mobile

### Category Badges (filter)
Six categories assigned to the existing 15 platforms:

| Badge | Color | Platforms |
|-------|-------|-----------|
| ☁️ Bulut | `#38bdf8` | Google Cloud, AWS, Microsoft Learn |
| 💻 Yazılım | `#6366f1` | freeCodeCamp, Linux Foundation |
| 🤖 AI & Veri | `#a855f7` | Kaggle, Hugging Face, Cognitive Class, NVIDIA DLI |
| 🔐 Güvenlik | `#f43f5e` | Cisco Networking Academy |
| 🎓 Akademik | `#22c55e` | ODTÜ Bilgeİş, BTK Akademi, IBM SkillsBuild |
| 🚀 Kariyer | `#fb923c` | Techcareer.net, İstanbul İşletme Enstitüsü |

Each platform in the `trainings` array gets a `category` field (one of: `bulut`, `yazilim`, `ai-veri`, `guvenlik`, `akademik`, `kariyer`).

### Search + Filter Logic
- `searchQuery` state (string) — filters by `title` or `description` (case-insensitive)
- `selectedCategory` state (string | null) — filters by `category`; null = show all
- Both filters apply simultaneously (AND)
- "X sonuç bulundu" count updates live
- Clicking active badge deselects it (toggle)

### Card Design
- Platform color accent on left border or icon background
- Icon wrapper: `background: ${color}20`, `color: ${color}`, 40x40px, `border-radius: 10px`
- Badge in top-right: category badge (same style as filter badges)
- CTA button: platform's own color (`background: ${training.color}`)
- No Bootstrap classes — use inline styles + CSS custom properties

---

## Page 2: SuggestionPage (`frontend/src/pages/SuggestionPage.jsx`)

### Layout
Two-column on desktop (`grid-template-columns: 3fr 2fr`), single column on mobile.

**Left column — Form:**
- Gradient heading "Bize Ulaş"
- Type selector: 4 toggle buttons (💡 Öneri, 🐛 Hata Bildirimi, 😤 Şikayet, 📌 Diğer) — replaces the `<select>`. Selected state: colored border + bg. Clicking sets `suggestion_type` in the form.
- Title input
- Description textarea
- Gradient submit button

**Right column — Info cards:**
Three cards stacked vertically:
1. 💡 Öneri — `rgba(99,102,241,0.08)` bg, purple border
2. 🐛 Hata Bildirimi — `rgba(244,63,94,0.08)` bg, red border
3. 📅 Etkinlik Talebi — `rgba(251,146,60,0.08)` bg, orange border, with "Talep Oluştur →" link button to `/etkinlik-talep`

### Form Behavior
- Type selector buttons replace `<select>` — one must be selected; clicking selects it and deselects others
- react-hook-form `setValue('suggestion_type', value)` on button click
- Validation, mutation, toast behavior unchanged

---

## Page 3: EventRequestPage (`frontend/src/pages/EventRequestPage.jsx`)

### Layout
Two-step wizard. Single centered column, max-width 560px.

**Step indicator:** Two steps with connecting line. Active step: filled `#38bdf8` circle. Completed step: checkmark. Inactive: `rgba(255,255,255,0.1)` circle.

**Step 1 — Etkinlik Linki:**
- Heading: "Etkinlik Linkini Gir"
- Subtitle: "URL'yi yapıştır, bilgiler otomatik doldurulacak"  
- URL input (required, validated)
- "Devam →" button — validates URL field, advances to step 2

**Step 2 — Detaylar:**
- Back button (← Geri) — returns to step 1
- Title input (required)
- Date input (optional)
- Description textarea (optional)
- Email input (optional) — "Geri dönüş için e-posta (isteğe bağlı)"
- "Gönder →" gradient button

### State
- `currentStep` state: `1 | 2`
- react-hook-form spans both steps — `handleSubmit` only called on step 2 submit
- Step 1 "Devam" triggers `trigger('event_link')` to validate before advancing
- On success toast: reset form + return to step 1

---

## Shared CSS Changes (`frontend/src/index.css`)

Add styles for:
- `.page-hero` — hero section wrapper with gradient title support
- `.filter-row` — search + badge filter row
- `.training-card` — card with platform color accent
- `.type-btn` — suggestion type toggle button (base + selected state)
- `.step-indicator` — wizard progress bar wrapper
- `.step-circle` — individual step circle (active/completed/inactive variants)
- `.wizard-form-card` — card wrapper for wizard steps

All new classes must respect `[data-theme="light"]` overrides where background colors differ.

---

## Out of Scope
- No backend changes
- No new API endpoints
- No changes to admin pages
- No routing changes
