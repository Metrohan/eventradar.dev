# TechEventRadar

TechEventRadar, turkiye odakli teknoloji etkinliklerini (bootcamp, hackathon, program vb.) farkli kaynaklardan cekip tek yerde listeleyen Flask tabanli bir uygulamadir.

## Ozellikler

- Coklu scraper kaynagi (TechCareer, Coderspace, Anbean, Kodluyoruz, Youthall)
- PostgreSQL uzerinde kalici veri saklama
- Web arayuzu uzerinden etkinlik listeleme
- Manuel veri guncelleme akisi (`run_daily_scrape.py`)
- Docker Compose ile hizli ayaga kaldirma

## Teknoloji

- Python, Flask
- SQLAlchemy, PostgreSQL
- Selenium, BeautifulSoup
- Docker, Docker Compose

## Hızlı Baslangic

### 1) Kurulum

```bash
git clone https://github.com/Metrohan/TechEventRadarOpenSource.git
cd TechEventRadarOpenSource
cp .env.example .env
```

### 2) Docker ile calistir

```bash
docker compose up --build -d
```

Uygulama: `http://localhost:5000`

### 3) Veri cekimini calistir

```bash
docker compose exec app python run_daily_scrape.py
```

Alternatif (lokal python):

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python app.py
```

## Ortam Degiskenleri

Gerekli degiskenler icin `.env.example` dosyasini kullanin.

- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_HOST`
- `FLASK_SECRET_KEY`
- `SQLALCHEMY_DATABASE_URI`
- `ADMIN_USERNAME`
- `ADMIN_PASSWORD`
- `SIMILARITY_THRESHOLD`

## Proje Yapisi

```text
TechEventRadarOpenSource/
  app.py
  run_daily_scrape.py
  config.py
  docker-compose.yml
  Dockerfile
  models/
  routes/
  services/
  scrapers/
  templates/
  static/
  utils/
```

## Open Source Notlari

- Katki sureci: `CONTRIBUTING.md`
- Lisans: `LICENSE` (MIT)
- Guvenlik bildirimi: `SECURITY.md`
- Davranis kurallari: `CODE_OF_CONDUCT.md`

## Guvenlik

- Gercek gizli bilgileri (`.env`) repoya commit etmeyin.
- Paylasim icin sadece `.env.example` kullanin.
- Scraper kullanirken hedef sitelerin kosullarina uyun.
