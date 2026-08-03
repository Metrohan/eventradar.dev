# TASK-015-repo-hygiene: Release artifact'larını ayır, workspace dosyalarını yoksay

## Problem

Pek çok proje dosyası (AGENTS.md, justfile, script'ler, task dosyaları, agent tanımları)
untracked kalıyordu. Bazı workspace artifact'ları (.coverage, .meto-ai/) ise gitignore'a
alınmamıştı — `git status` gereksiz dosyalarla doluyordu.

## Goal

- Proje belgelerine ait dosyaları `git add` ile takibe al
- Kişisel workspace artifact'larını `.gitignore`'a ekle

## Acceptance criteria

- [x] `.gitignore` — `.coverage` ve `.meto-ai/` eklendi
- [x] `.claude/agents/` — 9 agent tanımı takibe alındı (proje genelinde paylaşımlı)
- [x] `.githooks/` — pre-commit ve pre-push hook'ları takibe alındı
- [x] `.github/copilot-instructions.md` — takibe alındı
- [x] `AGENTS.md` — takibe alındı
- [x] `justfile` — takibe alındı
- [x] `docs/CURRENT_STATE.md`, `DECISIONS.md`, `TROUBLESHOOTING.md` — takibe alındı
- [x] `scripts/create-handoff-context.sh`, `scripts/create-task.sh` — takibe alındı
- [x] `tasks/active/TASK-028-i18n-close/CONTEXT.md` — takibe alındı

## Out of scope

- `.claude/settings.local.json` — zaten .gitignore'da, kişisel ayar

## Commit

`345d02f` — `chore(repo): track project docs/scripts, ignore workspace artifacts` — Closes #15
