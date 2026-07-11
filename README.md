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

<p>
  <a href="https://eventradar.dev"><img src="https://img.shields.io/badge/🌐_Canlı_Siteyi_Ziyaret_Et-eventradar.dev-38BDF8?style=for-the-badge" alt="Canlı Site"></a>
  <a href="CONTRIBUTING.md"><img src="https://img.shields.io/badge/🤝_Katkı_Sağla-Rehberi_Oku-22C55E?style=for-the-badge" alt="Katkı Sağla"></a>
  <a href="https://github.com/Metrohan/eventradar.dev/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22"><img src="https://img.shields.io/github/issues/Metrohan/eventradar.dev/good%20first%20issue?style=for-the-badge&label=Good%20First%20Issue&color=A855F7" alt="Good First Issue"></a>
</p>

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
| Tech Istanbul | ✅ Aktif | ✗ |

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

### İlk Katkını Seç

`good first issue` etiketli, kolay başlangıç için hazırlanmış açık işler:

- [#46 Event detail page retries 404 responses unnecessarily](https://github.com/Metrohan/eventradar.dev/issues/46)
- [#42 Login error message hardcoded in English while rest of app is Turkish](https://github.com/Metrohan/eventradar.dev/issues/42)
- [#37 Expand AnalyticsService test coverage for get_stats edge cases](https://github.com/Metrohan/eventradar.dev/issues/37)
- [#36 Fix redundant alt text on GitHub icon in Header](https://github.com/Metrohan/eventradar.dev/issues/36)
- [#34 Add aria-label to theme toggle button](https://github.com/Metrohan/eventradar.dev/issues/34)

Daha fazlası için: [tüm `good first issue` etiketli işler](https://github.com/Metrohan/eventradar.dev/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)

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

> **Uzun vadeli hedef:** TechEventRadar'ı yalnızca Türkiye'ye değil, dünyanın her ülkesinden teknoloji etkinliklerini çekebilen, geliştiricilerin küresel fırsatları tek yerden keşfedebildiği bir platforma dönüştürmek.

### Faz 1 — Temel ✅ (Tamamlandı)
- [x] Çoklu kaynaklardan otomatik etkinlik toplama (8 kaynak)
- [x] Kategori tag sistemi (Hackathon, Bootcamp, Seminer…)
- [x] Admin paneli ve içerik yönetimi
- [x] Telegram bildirim sistemi
- [x] CI/CD pipeline ve test altyapısı

### Faz 2 — Kalite & Güvenilirlik 🔧 (Devam ediyor)
- [ ] Yeni Türkçe kaynaklar: Skillcamp/Patika, Komunite
- [ ] Scraper'lara retry mekanizması ve hata yönetimi
- [ ] Kaynak bazlı kalite metrikleri (başarı oranı, veri tamlığı)
- [ ] Konum verisi normalizasyonu (Online / şehir bazlı)
- [ ] Geçmiş etkinliklerin otomatik arşivlenmesi

### Faz 3 — Ürün Büyümesi 🚀 (Yakın dönem)
- [ ] Kullanıcı hesabı ve kişiselleştirilmiş etkinlik önerileri
- [ ] E-posta / tarayıcı bildirim abonelikleri
- [x] Gelişmiş arama ve filtreleme (şehir, tarih aralığı, ücret)
- [ ] Etkinlik takvimi görünümü
- [ ] Mobil uyumlu PWA

### Faz 4 — Uluslararasılaşma 🌍 (Uzun dönem)
- [ ] Çok dilli arayüz (TR / EN)
- [ ] Ülke ve bölge bazlı filtreleme
- [ ] Uluslararası kaynak entegrasyonları (Eventbrite, Luma, Devpost…)
- [ ] Herhangi bir ülkenin tech etkinliklerini çekebilen adaptör mimarisi
- [ ] Global etkinlik haritası

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

## Destek / Sponsorship

TechEventRadar tamamen ücretsiz ve açık kaynak. Domain ve sunucu maliyetlerini karşılamak için desteğine ihtiyacımız var.

> Bu projeyi faydalı buluyorsan, bir kahve ısmarlayarak sürdürülebilirliğine katkıda bulunabilirsin.

[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-ffdd00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/metehangnn)
[![GitHub Sponsors](https://img.shields.io/badge/GitHub%20Sponsors-EA4AAA?style=for-the-badge&logo=github-sponsors&logoColor=white)](https://github.com/sponsors/Metrohan)

**Nereye gidiyor?**
- `eventradar.dev` domain yenileme (~1.000 TL/yıl)
- Sunucu barındırma maliyetleri

---

## Katkıda Bulunanlar

Projeye katkıda bulunan herkese teşekkürler! Bu liste her main push'unda [contributors-readme-action](https://github.com/akhilmhdh/contributors-readme-action) tarafından otomatik güncellenir.

<!-- readme: contributors -start -->
<table>
	<tbody>
		<tr>
            <td align="center">
                <a href="https://github.com/Metrohan">
                    <img src="https://avatars.githubusercontent.com/u/54481595?v=4" width="64;" alt="Metrohan"/>
                    <br />
                    <sub><b>Metrohan</b></sub>
                </a>
            </td>
            <td align="center">
                <a href="https://github.com/4ykutG">
                    <img src="https://avatars.githubusercontent.com/u/111429441?v=4" width="64;" alt="4ykutG"/>
                    <br />
                    <sub><b>4ykutG</b></sub>
                </a>
            </td>
            <td align="center">
                <a href="https://github.com/onurege3467">
                    <img src="https://avatars.githubusercontent.com/u/78586675?v=4" width="64;" alt="onurege3467"/>
                    <br />
                    <sub><b>onurege3467</b></sub>
                </a>
            </td>
            <td align="center">
                <a href="https://github.com/aqilaziz">
                    <img src="https://avatars.githubusercontent.com/u/46887634?v=4" width="64;" alt="aqilaziz"/>
                    <br />
                    <sub><b>aqilaziz</b></sub>
                </a>
            </td>
            <td align="center">
                <a href="https://github.com/blut-agent">
                    <img src="https://avatars.githubusercontent.com/u/278569635?v=4" width="64;" alt="blut-agent"/>
                    <br />
                    <sub><b>Blut-agent</b></sub>
                </a>
            </td>
            <td align="center">
                <a href="https://github.com/rashmitha-j">
                    <img src="https://avatars.githubusercontent.com/u/223723538?v=4" width="64;" alt="rashmitha-j"/>
                    <br />
                    <sub><b>rashmitha-j</b></sub>
                </a>
            </td>
		</tr>
	<tbody>
</table>
<!-- readme: contributors -end -->
