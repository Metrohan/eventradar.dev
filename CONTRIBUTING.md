# Contributing to EventRadar

Bu projeye katkıda bulunmak istediğin için teşekkürler! Her türlü katkı değerlidir.

## Getting Started

1. Repoyu fork et
2. Fork'u klonla: `git clone https://github.com/YOUR_USER/eventradar.dev.git`
3. Branch oluştur: `git checkout -b feat/my-feature`
4. Env dosyasını kopyala: `cp .env.example .env` ve değerleri doldur
5. Backend bağımlılıkları: `pip install -r requirements.txt -r requirements-dev.txt`
6. Frontend bağımlılıkları: `cd frontend && npm install`
7. Değişikliklerini yap ve testleri yaz
8. Doğrula: `pytest -m "not integration"` ve `black --check .`
9. Commit et ve PR aç

## Branch Naming

- `feat/description` — yeni özellik
- `fix/description` — hata düzeltmesi
- `docs/description` — sadece dokümantasyon
- `scraper/source-name` — yeni veya düzeltilmiş scraper
- `refactor/description` — davranış değişikliği olmadan kod temizliği

## Pre-PR Checklist

- [ ] `pytest -m "not integration"` geçiyor
- [ ] `black .` formatting uygulandı
- [ ] Yeni pylint hatası eklenmedi
- [ ] PR açıklaması neyin neden değiştiğini açıklıyor

## Adding a New Scraper

1. `app/scrapers/<name>_scraper.py` oluştur
2. `scrape_<name>_events() -> List[Dict]` fonksiyonunu implemente et
   - Her dict'te şunlar **zorunlu**: `title` (str), `url` (str, unique), `source` (str)
   - Opsiyonel: `description`, `date`, `location`, `image_url`
3. `app/services/scraper_service.py` içindeki `ScraperService.SCRAPER_FUNCS`'a kaydet
4. `tests/fixtures/<name>.html` dosyasına örnek HTML ekle
5. `tests/unit/test_scrapers.py` dosyasına mock unit test ekle

## Bug Reports & Feature Requests

[GitHub Issues](https://github.com/Metrohan/eventradar.dev/issues) üzerinden bildir.

---

*Commit mesajları için [Conventional Commits](https://www.conventionalcommits.org/) formatı önerilir.*
