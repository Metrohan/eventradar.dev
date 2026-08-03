# TASK-036-coffee-a11y: SupportModal coffee icon'unu dekoratif yap

## Problem

`SupportModal.jsx` içindeki kahve SVG görseli `alt="Coffee"` attribute'u ile render ediliyordu.
"Buy Me A Coffee" link metni yanındaki bu icon, screen reader'larda "Coffee Buy Me A Coffee"
olarak okunuyordu — gereksiz tekrar.

## Goal

Dekoratif icon'lar `alt=""` ile işaretlenmeli (WCAG 2.1 — decorative images).
Aynı pattern `Header.jsx`'te zaten uygulanmış.

## Acceptance criteria

- [x] `SupportModal.jsx` — kahve SVG'si `alt=""` ile işaretlendi

## In scope

- `frontend/src/components/SupportModal.jsx` — tek satır

## Out of scope

- Başka component'lardaki icon'lar (zaten doğru)

## Commit

`f075bd1` — `fix(a11y): make coffee icon decorative in SupportModal` — Closes #36
