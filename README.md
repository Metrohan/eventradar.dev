# TechEventRadar

[![Tests](https://github.com/Metrohan/eventradar.dev/actions/workflows/test.yml/badge.svg)](https://github.com/Metrohan/eventradar.dev/actions/workflows/test.yml)
[![Deploy](https://github.com/Metrohan/eventradar.dev/actions/workflows/deploy.yml/badge.svg)](https://github.com/Metrohan/eventradar.dev/actions/workflows/deploy.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/docker-compose-2496ED?logo=docker&logoColor=white)](docker-compose.yml)

[English README](README.en.md)

Tek cümle amaç: **Öğrencilerin ve yeni mezunların güncel teknoloji etkinliklerini tek yerde kolayca bulması.**

TechEventRadar; bootcamp, webinar, hackathon, kariyer etkinliği ve topluluk buluşmalarını farklı kaynaklardan toplayıp tek bir ekranda sunar. Böylece öğrenciler "hangi etkinlik ne zaman, nerede, nasıl başvurulur" sorularını tek tek siteleri gezmeden yanıtlayabilir.

![TechEventRadar Logo](frontend/public/techeventradar_logo.png)

## Neden Bu Proje?

Öğrenciler için en büyük problem bilgiden çok **dağınıklık**:

- Etkinlikler farklı platformlara dağılmış durumda
- Son başvuru tarihleri kolayca kaçırılıyor
- Ücretsiz/online etkinlikleri filtrelemek zaman alıyor

TechEventRadar bu dağınıklığı azaltmak için geliştirildi.

## Öne Çıkan Özellikler

- Çoklu kaynaklardan etkinlik toplama
- **Kategori tag sistemi** — Hackathon, Seminer/Webinar, Atölye, Konferans, Bootcamp badge'leriyle filtreleme
- Tek listede arama ve filtreleme
- Etkinlik detayına hızlı erişim
- Admin paneli ile içerik yönetimi
- Öneri/şikayet ve etkinlik ekleme talepleri
- Duyuru sistemi

**🌐 Canlı Demo:** [eventradar.dev](https://eventradar.dev)

![TechEventRadar ana sayfa ekran görüntüsü](docs/assets/eventradar-homepage.png)

## Mimari

```text
┌─────────────────────────────────────────────────────────┐
│                  Frontend (React + Vite)                 │
│                    http://localhost:3000                  │
└──────────────────────────┬──────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────┐
│                 Backend (FastAPI)                        │
│                  http://localhost:8000                   │
│       /api/events  /api/admin  /health  /docs            │
└──────────┬─────────────────────────────┬────────────────┘
           │                             │
  ┌────────▼────────┐          ┌─────────▼─────────┐
  │   PostgreSQL    │          │     Scrapers       │
  │  (Events DB)    │          │  youthall, akbank  │
  └─────────────────┘          │  techcareer, ...   │
                               └────────────────────┘
```

- **Backend:** FastAPI + SQLAlchemy + PostgreSQL
- **Frontend:** React (Vite)
- **Scraping:** Python tabanlı scraper modülleri (Selenium + requests)
- **Deployment:** Docker Compose

## Hızlı Başlangıç (Docker)

```bash
git clone https://github.com/Metrohan/eventradar.dev.git
cd eventradar.dev
cp .env.example .env
# .env içinde SECRET_KEY, ADMIN_USERNAME, ADMIN_PASSWORD değerlerini düzenle
docker compose up -d --build
sleep 10
curl http://localhost:8000/health
# Frontend: http://localhost:3000
```

## Scrapers

| Kaynak | Durum | Selenium |
|--------|-------|----------|
| TechCareer | ✅ Aktif | ✓ |
| Youthall | ✅ Aktif | ✓ |
| Akbank Gençlik | ✅ Aktif | ✓ (UC) |
| Pupilica | ✅ Aktif | ✓ (UC) |
| Kodluyoruz | ✅ Aktif | ✗ |
| Anbean | ✅ Aktif | ✗ |
| Coderspace | ✅ Aktif | ✓ (UC) |

## API Docs

- Swagger UI: <http://localhost:8000/docs>
- Health check: <http://localhost:8000/health>

## Troubleshooting

**Port 8000 zaten kullanımda:**

```bash
lsof -i :8000
kill -9 <PID>
```

**Database connection error:**
`.env` içindeki `DATABASE_URL` değerinin `docker-compose.yml`'deki servis adıyla eşleştiğini kontrol et.

**Scraper Chrome hatası:**
Scraper logları için: `GET /api/admin/scraper-logs` (admin token gerekli)

## Geliştirme (Local)

### Backend

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Testler

```bash
pip install -r requirements-dev.txt
pytest -m "not integration"          # Unit testler
pytest -m integration                # Gerçek scraper testleri (Chrome gerekli)
```

## Katkı Sağlama

Katkıların proje için çok değerli. Küçük düzeltmeler bile büyük etki oluşturur.

### Nasıl katkı verebilirsin?

- Yeni scraper kaynağı eklemek
- Mevcut scraper hatalarını düzeltmek
- Tarih/konum ayrıştırma doğruluğunu artırmak
- Frontend filtreleme ve UX iyileştirmeleri
- Dokümantasyon ve test kapsamını geliştirmek

### Adım adım katkı akışı

1. Bu repoyu fork et
2. Yeni bir branch aç
3. Değişikliğini yap
4. Test et
5. Açıklayıcı bir Pull Request gönder

Örnek:

```bash
git checkout -b feat/add-new-source
git add .
git commit -m "feat: add new event source scraper"
git push origin feat/add-new-source
```

Daha detaylı rehber için: [CONTRIBUTING.md](CONTRIBUTING.md)

## Güvenlik ve Gizlilik

Bu proje açık kaynak sürümde secret/credential içermez. Şüpheli bir güvenlik problemi görürsen lütfen [SECURITY.md](SECURITY.md) üzerinden bildir.

## Yol Haritası

- Kaynak sayısını artırmak
- Daha sağlam tarih normalizasyonu
- Kalite metrikleri (kaynak bazlı başarı oranı)
- Öğrenci dostu kişiselleştirilmiş öneri sistemi

## Lisans

MIT Lisansı: [LICENSE](LICENSE)

---

Bu proje öğrencilerin fırsatlara daha hızlı ulaşabilmesi için geliştiriliyor. İyi bir etkinlik bazen kariyerin yönünü değiştirir.

## Scraper'ı Manuel Çalıştırma

Etkinlikleri anlık çekmek için:

```bash
docker compose run --rm scraper python scripts/run_daily_scrape.py
```

## Hata Alarmı (Telegram)

`backend`/`scraper` loglarında kritik hata olduğunda Telegram mesajı almak için:

```bash
export TELEGRAM_BOT_TOKEN="<BOT_TOKEN>"
export TELEGRAM_CHAT_ID="<CHAT_ID>"
python3 scripts/monitor_alerts.py
```

Sürekli izleme için cron örneği (her 2 dakikada bir):

```bash
*/2 * * * * cd /path/to/eventradar.dev && TELEGRAM_BOT_TOKEN=<BOT_TOKEN> TELEGRAM_CHAT_ID=<CHAT_ID> /usr/bin/python3 scripts/monitor_alerts.py >> /var/log/eventradar-alerts.log 2>&1
```

---

## Katkıda Bulunanlar

Projeye katkıda bulunan herkese teşekkürler!

<table>
  <tr>
    <td align="center">
      <a href="https://github.com/Metrohan">
        <img src="https://github.com/Metrohan.png" width="64" alt="Metrohan"/><br/>
        <sub><b>Metrohan</b></sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/4ykutG">
        <img src="https://github.com/4ykutG.png" width="64" alt="4ykutG"/><br/>
        <sub><b>4ykutG</b></sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/onurege3467">
        <img src="https://github.com/onurege3467.png" width="64" alt="onurege3467"/><br/>
        <sub><b>onurege3467</b></sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/aqilaziz">
        <img src="https://github.com/aqilaziz.png" width="64" alt="aqilaziz"/><br/>
        <sub><b>aqilaziz</b></sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/rashmitha-j">
        <img src="https://github.com/rashmitha-j.png" width="64" alt="rashmitha-j"/><br/>
        <sub><b>rashmitha-j</b></sub>
      </a>
    </td>
  </tr>
</table>
