<img width="802" height="420" alt="TechEventRadar Banner" src="https://github.com/user-attachments/assets/7528bb63-f02d-48cf-9cb9-f22e822128dd" />

# 🚀 TechEventRadar

TechEventRadar, Türkiye'deki çeşitli teknoloji ve kariyer platformlarını tarayarak en güncel etkinlikleri, bootcamp'leri ve hackathon'ları tek bir noktada toplayan modern ve açık kaynaklı bir platformdur. En temel amacı yazılım/bilgisayar mühendisliği veya ilgili bölümlere yeni başlayan öğrencilere bilgi vermek ve onları ilerideki sektörlerde başarılı olmalarına yardımcı olmasını sağlamaktır.

Bu sürüm, **FastAPI** backend ve **React (Vite)** frontend mimarisi ile tamamen yenilenmiştir.

## ✨ Öne Çıkan Özellikler

*   **🌓 Koyu/Açık Tema Desteği:** Kullanıcılar tercihlerine göre karanlık veya aydınlık mod arasında kolayca geçiş yapabilir.
*   **📚 Ücretsiz Eğitimler:** Sektörün devlerinden (Google, AWS, Microsoft, IBM) küratörlüğünü yaptığımız ücretsiz eğitim kaynakları.
*   **📣 Kullanıcı Katılımı:** Sayfa üzerinden yeni etkinlik talepleri gönderebilir, öneri ve şikayetlerinizi iletebilirsiniz.
*   **🛠️ Admin Kontrol Paneli:** Gelişmiş admin paneli ile scraper'ları tetikleyebilir, logları izleyebilir ve bildirimleri yönetebilirsiniz.
*   **🛡️ Gelişmiş Scraper'lar:** `undetected-chromedriver` entegrasyonu ile Cloudflare korumalı sitelerden bile sorunsuz veri çekimi.
*   **🤖 Otomatik Tarih Ayrıştırma:** Dağınık tarih formatlarını (D/M/YYYY, Türkçe aylar vb.) otomatik olarak standart veritabanı formatına dönüştürür.

## 🛠️ Teknolojiler

### Backend
- **FastAPI:** Yüksek performanslı, modern Python web çatısı.
- **PostgreSQL:** İlişkisel veritabanı.
- **SQLAlchemy:** ORM katmanı.
- **Alembic:** Veritabanı migrasyon yönetimi.
- **dateparser:** Esnek tarih ayrıştırma.

### Scrapers
- **Selenium / undetected-chromedriver:** Dinamik içerikleri çekmek için.
- **BeautifulSoup4:** HTML analizi.

### Frontend
- **React (Vite):** Hızlı ve modern web arayüzü.
- **ThemeContext:** Tema yönetimi ve yerel depolama entegrasyonu.
- **Bootstrap 5 / Vanilla CSS:** Modern ve duyarlı tasarım.

## 🚀 Kurulum ve Çalıştırma

### Docker ile Hızlı Kurululm

1.  **Repoyu Klonlayın:**
    ```bash
    git clone https://github.com/Metrohan/eventradar.dev.git
    cd eventradar.dev
    ```

2.  **Docker Ortamını Başlatın:**
    ```bash
    docker-compose up --build -d
    ```

3.  **Başlangıç Scraper'ını Çalıştırın:**
    ```bash
    docker exec techeventradar_backend python scripts/run_daily_scrape.py
    ```

### Yerel Geliştirme (Opsiyonel)

- **Backend:** `requirements.txt` dosyasındaki bağımlılıkları yükleyin ve `uvicorn app.main:app --reload` ile başlatın.
- **Frontend:** `frontend` klasörüne girin, `npm install` ve `npm run dev` komutlarını çalıştırın.

## 📂 Proje Yapısı

```
eventradar.dev/
├── app/                # FastAPI Backend Uygulaması
│   ├── api/            # API Endpointleri
│   ├── core/           # Konfigürasyon ve DB Ayarları
│   ├── models/         # DB Modelleri
│   ├── services/       # İş Mantığı
│   └── scrapers/       # Site bazlı kazıyıcılar
├── frontend/           # React (Vite) Frontend
│   └── src/            # Bileşenler, Sayfalar, Contextler
├── scripts/            # Bakım ve scraping scriptleri
├── docker-compose.yml  # Docker orkestrasyonu
└── requirements.txt    # Python bağımlılıkları
```

## 🤝 Katkıda Bulunma

Projeye katkıda bulunmak isterseniz bir **Pull Request** açabilir veya karşılaştığınız hataları **Issue** olarak bildirebilirsiniz.

## 📜 Lisans

Bu proje **MIT Lisansı** altında lisanslanmıştır.
