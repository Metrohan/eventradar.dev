# HANDOFF — TASK-016-integration-tests

## Durum: Planning — implementation başlamadı

## Araştırma Özeti

`pytest.ini` addopts'a `-m "not integration"` eklemek **çalışmaz** çünkü:
- `pytest -m integration` çalıştırıldığında addopts + CLI aynı anda uygulanır
- pytest bunları AND'ler: `"not integration" AND "integration"` → hiçbir test çalışmaz

## Seçilen Yaklaşım

`tests/conftest.py`'ye `pytest_collection_modifyitems` hook'u ekle:

```python
def pytest_collection_modifyitems(config, items):
    if not config.getoption("-m", default="").strip():
        skip_marker = pytest.mark.skip(reason="use -m integration to run live scraper tests")
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip_marker)
```

Bu yaklaşım:
- `pytest` → integration testler SKIP
- `pytest -m integration` → integration testler çalışır
- CI'daki `-m "not integration"` → değişmeden çalışmaya devam eder

## Sonraki Kesin İşlem

1. `tests/conftest.py`'yi oku (okundu ama içerik tam görülmedi)
2. Hook'u dosyanın sonuna ekle (mevcut `test_db` fixture'dan sonra)
3. Doğrulama komutları:
   ```bash
   ./venv/bin/python -m pytest --collect-only -q 2>&1 | grep -i "skip\|integr"
   ./venv/bin/python -m pytest tests/unit/ -q --no-header
   ```
4. Commit: `fix(ci): skip integration tests by default in pytest — Closes #16`

## Risk

Sıfır production riski — yalnızca test toplama davranışı değişiyor.
