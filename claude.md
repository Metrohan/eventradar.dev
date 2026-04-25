# TechEventRadar - Claude Çalışma Rehberi

Bu doküman, bu repoda çalışan bir AI asistanı için kısa ve pratik bir bağlam sağlar.

## Proje Özeti

- Amaç: Teknoloji etkinliklerini farklı kaynaklardan çekip tek platformda sunmak.
- Mimari: FastAPI + SQLAlchemy + PostgreSQL + React (Vite).
- Ana akış: Scraper veriyi toplar, backend API sunar, frontend `/api` üzerinden tüketir.

## Dizin Yapısı

- `app/`: Backend kodu (API, core, models, services, scrapers).
- `frontend/`: React uygulaması.
- `alembic/`: Veritabanı migration dosyaları.
- `scripts/`: Scraper, test ve operasyon scriptleri.
- `docker-compose.yml`: Lokal/servis orkestrasyonu.

## Hızlı Çalıştırma

```bash
cp .env.example .env
docker compose up -d --build
```

Servisler:

- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`

## Local Geliştirme

Backend:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

## Veritabanı ve Migration

Alembic, `DATABASE_URL` env değişkenini öncelikli kullanır (`alembic/env.py`).

Sık kullanılan komutlar:

```bash
alembic upgrade head
alembic revision --autogenerate -m "short_description"
alembic downgrade -1
```

Not:

- `alembic.ini` içindeki `sqlalchemy.url` varsayılan fallback değerdir.
- Üretim/lokal doğru veritabanı için `DATABASE_URL` mutlaka doğrulanmalı.

## API Notları

- Frontend API base: `/api` (`frontend/src/services/api.js`).
- Public event list endpoint'i: `GET /api/events`.
- Beklenen event list response alanları: `events`, `total_count`, `last_updated`.
- Health endpoint: `GET /health`.

## Scraper Akışı

Manuel scrape:

```bash
docker compose run --rm scraper python scripts/run_daily_scrape.py
```

Test scriptleri `scripts/` altında bulunur (`test_scrapers.py`, `test_sequential_scrape.py` vb.).

## Güvenlik ve Konfigürasyon

- `SECRET_KEY`, `ADMIN_USERNAME`, `ADMIN_PASSWORD` boş/geçersizken uygulama varsayılan olarak açılmaz (`app/core/config.py`).
- Secret bilgileri repoya commit edilmemeli; sadece `.env` üzerinden yönetilmeli.

## Kodlama Beklentisi

- Küçük ve odaklı değişiklikler yap.
- Mevcut kod stilini ve klasör organizasyonunu koru.
- Davranış değiştiren düzenlemelerde ilgili script/test ile doğrulama yap.
- Frontend değişikliği yaptıysan en azından ilgili sayfayı manuel smoke test et.

## PR / Commit Pratiği

- Branch isimleri: `fix/...`, `feat/...`, `chore/...`
- Commit formatı: Conventional Commits önerilir.
- PR açıklamasında: ne değişti, neden değişti, nasıl test edildi net yazılmalı.

## Sorun Giderme Kısa Notları

- Frontend veri göstermiyor ama backend sağlıklıysa önce `/api` proxy ve response şemasını kontrol et.
- `503/502` görüldüğünde servis health ve reverse proxy yönlendirmesi birlikte doğrulanmalı.
- Migration hatalarında ilk kontrol: yanlış/verimsiz `DATABASE_URL`.
