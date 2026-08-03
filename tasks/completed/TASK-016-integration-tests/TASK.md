# TASK-016-integration-tests: Scraper integration testlerini CI'da opsiyonel yap

## Problem

`pytest.ini` `addopts` satırı `-m "not integration"` içermiyor. Bu yüzden:
- `pytest` komutu çalıştırıldığında live scraper testleri de çalışıyor
- Bu testler gerçek internet bağlantısı gerektirir, CI'da güvensiz ve yavaş
- `CONTRIBUTING.md` zaten `pytest -m "not integration"` kullanımını belgeliyor
  ama enforcement yok

## Durum: Araştırma tamamlandı, implementation YOK

Önceki session'da `conftest.py` okundu ancak değişiklik yapılmadan session sona erdi.

## Doğrulanan Gerçekler

- `pytest.ini` `addopts = --cov=app --cov-report=xml --cov-fail-under=70`
- `markers = integration: marks tests as integration tests (deselect with '-m "not integration"')`
- `tests/integration/test_scrapers_real.py` — tüm testler `@pytest.mark.integration` ile işaretli
- CI (`test.yml`) zaten `pytest -m "not integration" --cov=app --cov-report=xml -q` kullanıyor
- `CONTRIBUTING.md` zaten `pytest -m "not integration"` kullanımını belgeliyor

## Kritik Kısıt

`addopts`'a `-m "not integration"` eklenirse, local'de `pytest -m integration` çalıştırılınca
pytest `(-m "not integration") AND (-m "integration")` uygular → hiçbir test çalışmaz.

**Önerilen Çözüm:** `conftest.py`'ye hook ekle:

```python
def pytest_collection_modifyitems(config, items):
    if not config.getoption("-m", default="").strip():
        # No explicit -m filter given — skip integration by default
        skip_integration = pytest.mark.skip(reason="use -m integration to run live scraper tests")
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip_integration)
```

Bu yaklaşımda:
- `pytest` → integration testler otomatik skip
- `pytest -m integration` → yalnızca integration testler çalışır (addopts çakışması yok)
- CI'daki mevcut `-m "not integration"` değişmeden çalışmaya devam eder

## Acceptance criteria

- [ ] `pytest` komutu çalıştırıldığında integration testler varsayılan olarak skip edilir
- [ ] `pytest -m integration` komutu live scraper testlerini çalıştırır
- [ ] CI workflow değişikliği gerekmez (zaten `-m "not integration"` kullanıyor)
- [ ] `pytest --cov-fail-under=70` hâlâ geçiyor (integration testler hariç)
- [ ] Değişiklik `CONTRIBUTING.md`'de belgeleniyor

## In scope

- `tests/conftest.py` — `pytest_collection_modifyitems` hook'u ekle
- `CONTRIBUTING.md` — açıklama güncelle (opsiyonel)

## Out of scope

- `pytest.ini addopts` değişikliği (çakışma riski var)
- CI workflow değişikliği (zaten doğru)
- Test ekleme/kaldırma

## Sonraki Kesin İşlem

1. `tests/conftest.py`'ye `pytest_collection_modifyitems` hook'u ekle
2. `./venv/bin/python -m pytest --collect-only 2>/dev/null | grep integration` → testlerin skip olduğunu doğrula
3. `./venv/bin/python -m pytest tests/unit/ -q` → coverage check geçiyor mu doğrula
4. Commit: `fix(ci): skip integration tests by default in pytest`
5. GitHub issue #16'yı kapat
