# Contributing to EventRadar

**[English below](#contributing-to-eventradar-english)**

---

## Katkıda Bulunma (Türkçe)

Bu projeye katkıda bulunmak istediğin için teşekkürler! Her türlü katkı değerlidir.

### Başlangıç

1. Repoyu fork et
2. Fork'u klonla: `git clone https://github.com/YOUR_USER/eventradar.dev.git`
3. Branch oluştur: `git checkout -b feat/my-feature`
4. Env dosyasını kopyala: `cp .env.example .env` ve değerleri doldur
5. Backend bağımlılıkları: `pip install -r requirements.txt -r requirements-dev.txt`
6. Frontend bağımlılıkları: `cd frontend && npm install`
7. Değişikliklerini yap ve testleri yaz
8. Doğrula: `pytest -m "not integration"` ve `black .`
9. Commit et ve PR aç

### Branch İsimlendirme

| Prefix | Kullanım |
|---|---|
| `feat/` | yeni özellik |
| `fix/` | hata düzeltmesi |
| `docs/` | sadece dokümantasyon |
| `scraper/` | yeni veya düzeltilmiş scraper |
| `refactor/` | davranış değişikliği olmadan kod temizliği |

### PR Öncesi Kontrol Listesi

- [ ] `pytest -m "not integration"` geçiyor
- [ ] `black .` formatting uygulandı
- [ ] Yeni pylint hatası eklenmedi
- [ ] PR açıklaması neyin neden değiştiğini açıklıyor

### Yeni Scraper Ekleme

1. `app/scrapers/<name>_scraper.py` oluştur
2. `scrape_<name>_events() -> List[Dict]` fonksiyonunu implemente et
   - Her dict'te şunlar **zorunlu**: `title` (str), `url` (str, unique), `source` (str)
   - Opsiyonel: `description`, `date`, `location`, `image_url`
3. `app/services/scraper_service.py` içindeki `ScraperService.SCRAPER_FUNCS`'a kaydet
4. `tests/fixtures/<name>.html` dosyasına örnek HTML ekle
5. `tests/unit/test_scrapers.py` dosyasına mock unit test ekle

---

## Contributing to EventRadar (English)

Thank you for your interest in contributing! All contributions are welcome.

### Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USER/eventradar.dev.git`
3. Create a branch: `git checkout -b feat/my-feature`
4. Copy the env file: `cp .env.example .env` and fill in the values
5. Install backend deps: `pip install -r requirements.txt -r requirements-dev.txt`
6. Install frontend deps: `cd frontend && npm install`
7. Make your changes and write tests
8. Verify: `pytest -m "not integration"` and `black .`
9. Commit and open a PR

### Running with Docker (easiest)

```bash
cp .env.example .env   # set SECRET_KEY (≥32 chars), ADMIN_USERNAME, ADMIN_PASSWORD
docker compose down && docker compose up -d --build
```

- Frontend: http://localhost:3000
- Backend / Swagger: http://localhost:8000/docs

### Branch Naming

| Prefix | Use for |
|---|---|
| `feat/` | new feature |
| `fix/` | bug fix |
| `docs/` | documentation only |
| `scraper/` | new or updated scraper |
| `refactor/` | code cleanup without behavior change |

### Pre-PR Checklist

- [ ] `pytest -m "not integration"` passes
- [ ] `black .` formatting applied
- [ ] No new pylint errors introduced
- [ ] PR description explains what changed and why

### Adding a New Scraper

1. Create `app/scrapers/<name>_scraper.py`
2. Implement `scrape_<name>_events() -> List[Dict]`
   - **Required** keys per event: `title` (str), `url` (str, unique), `source` (str)
   - Optional: `description`, `date`, `location`, `image_url`
3. Register in `ScraperService.SCRAPER_FUNCS` in `app/services/scraper_service.py`
4. Add a sample HTML fixture at `tests/fixtures/<name>.html`
5. Add a mock unit test in `tests/unit/test_scrapers.py`

### Bug Reports & Feature Requests

Open an issue on [GitHub Issues](https://github.com/Metrohan/eventradar.dev/issues).

---

*Commit messages: [Conventional Commits](https://www.conventionalcommits.org/) format recommended.*
