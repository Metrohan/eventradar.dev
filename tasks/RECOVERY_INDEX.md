# RECOVERY INDEX — 2026-08-03

Bu dosya, `feat/i18n-foundation` branch'indeki tüm issue'ları ve task'ları tek noktada özetler.
Kurtarma tarihi: 2026-08-03. Repository kanıtına dayanır; varsayım yoktur.

## Durum Tablosu

| Konuşmadaki İstek | Task ID | Tür | İlgili Commit | Değişen Dosyalar | Uygulama Durumu | Eksik Test | Sonraki İşlem |
|---|---|---|---|---|---|---|---|
| #28 ThemeToggle i18n + #34 aria-label | TASK-028 | Mevcut task | `1f4961f` | ThemeToggle.jsx, tr/en JSON | ✅ Commit edildi | Manuel browser test | Reviewer onayı |
| #42 Login error Türkçe | TASK-042 | Bağımsız task | `4422b38` | app/api/admin_auth.py | ✅ Commit edildi | Yok (test detail'i assert etmiyor) | Merge |
| #36 SupportModal coffee icon dekoratif | TASK-036 | Bağımsız task | `f075bd1` | SupportModal.jsx | ✅ Commit edildi | Yok | Merge |
| #37 Analytics test edge cases | TASK-037 | Bağımsız task | `7aa75f8` | test_analytics_service.py | ✅ Commit edildi + test çalıştırıldı | Yok | Merge |
| #23 Kullanıcıları kanal UI ile bilgilendir | TASK-023 | Bağımsız task | `570f04a` | ChannelsBanner.jsx, HomePage.jsx, Footer.jsx, JSON | ✅ Commit edildi | Manuel browser test | Merge |
| #15 Release artifact'larını ayır | TASK-015 | Bağımsız task | `345d02f` | .gitignore, 21 yeni dosya | ✅ Commit edildi | Yok | Merge |
| #16 Integration testleri CI'da opsiyonel | TASK-016 | Bağımsız task | `8227782` | tests/conftest.py | ✅ Commit edildi | Yok | Merge |
| #20 Auto-archive past events | — | Kod değişikliği yok | — | — | ✅ Zaten uygulanmış (EventService filter) | — | Issue kapat |
| #77 Mobile FCP/LCP | — | Kod değişikliği yok | — | — | ✅ PR #87 ile çözülmüş | — | Issue kapat |
| #76 Oversized images | — | Kod değişikliği yok | — | — | ✅ image_pipeline.py ile çözülmüş | — | Issue kapat |
| #29, #30, #31, #32 Uluslararası özellikler | — | Wontfix | — | — | ✅ Kapatıldı | — | Issue'ları wontfix kapat |
| #23 User accounts | — | Wontfix | — | — | ✅ Wontfix (TASK-023 ile değiştirildi) | — | Issue kapat |

## Uncommitted Değişiklikler

| Dosya | Değişiklik | Sebep | Task | Aciliyet |
|---|---|---|---|---|
| `CLAUDE.md` | +12 satır METO-AI adapter bloğu | Session-start hook ekledi | — | Commit edilebilir |
| `frontend/package-lock.json` | `"dev": true` metadata | npm metadata drift | — | Commit edilebilir (next chore commit) |
| `scripts/convert_images.sh` | Sadece file mode: 100644→100755 | Executable bit | — | Commit edilebilir |
| `scripts/verify_deploy.sh` | Sadece file mode: 100644→100755 | Executable bit | — | Commit edilebilir |
| `tasks/active/TASK-028-i18n-close/CONTEXT.md` | Auto-generated context | Session-start hook | TASK-028 | Commit edilebilir |

## Task Dizin Yapısı

```
tasks/
  active/
    TASK-028-i18n-close/     ← committed, pending review
    TASK-016-integration-tests/ ← YARIDAKİ GÖREV — implementation bekliyor
  completed/
    TASK-015-repo-hygiene/   ← committed, pending merge
    TASK-023-channels/       ← committed, pending merge
    TASK-036-coffee-a11y/    ← committed, pending merge
    TASK-037-analytics-tests/ ← committed, pending merge
    TASK-042-login-error/    ← committed, pending merge
  abandoned/
    (boş)
  _template/
```

## Branch Commit Özeti (main..HEAD)

```
345d02f  chore(repo): track project docs/scripts [TASK-015] ✅
570f04a  feat(ui): channel discovery banner [TASK-023] ✅
7aa75f8  test(analytics): edge case coverage [TASK-037] ✅
f075bd1  fix(a11y): coffee icon decorative [TASK-036] ✅
4422b38  fix(auth): login error Turkish [TASK-042] ✅
1f4961f  fix(i18n): ThemeToggle i18n + aria-label [TASK-028] ✅
ea17b99  fix(i18n): ErrorBoundary keys
... (i18n migration batch commits)
727ffef  Faz 5: TR/EN i18n foundation (#89)
```

## Codex'e Devredilecek Sonraki Task

**TASK-016-integration-tests** — `tests/conftest.py`'ye `pytest_collection_modifyitems` hook'u ekle.

Detaylar: `tasks/active/TASK-016-integration-tests/HANDOFF.md`

Uygulama adımları:
1. `tests/conftest.py` oku
2. Dosyanın sonuna hook ekle:
   ```python
   def pytest_collection_modifyitems(config, items):
       if not config.getoption("-m", default="").strip():
           skip_marker = pytest.mark.skip(reason="use -m integration to run live scraper tests")
           for item in items:
               if "integration" in item.keywords:
                   item.add_marker(skip_marker)
   ```
3. `./venv/bin/python -m pytest --collect-only -q 2>&1 | grep -i skip` doğrula
4. `./venv/bin/python -m pytest tests/unit/ -q` doğrula
5. Commit: `fix(ci): skip integration tests by default — Closes #16`
