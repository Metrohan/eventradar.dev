<img width="802" height="420" alt="Başlıksız(1)" src="https://github.com/user-attachments/assets/7528bb63-f02d-48cf-9cb9-f22e822128dd" />

# 🚀 TechEventRadar

Bu proje, çeşitli Türk teknoloji ve kariyer platformlarından güncel etkinlikleri (bootcamp'ler, hackathon'lar, yetenek programları vb.) çekmek, **PostgreSQL veritabanında** depolamak ve kullanıcı dostu bir web arayüzünde sunmak için geliştirilmiştir. Python, Selenium, BeautifulSoup, Flask, **PostgreSQL, Nginx ve uWSGI** teknolojilerini kullanır.

## ✨ Özellikler

* **Çoklu Kaynak Desteği:** TechCareer.net, Coderspace, Anbean, Kodluyoruz, Youthall gibi platformlardan veri çekme yeteneği.
* **Dinamik Veri Çekimi:** Selenium kullanarak JavaScript ile yüklenen dinamik içerikleri sorunsuz bir şekilde işler.
* **Sağlam Veri Depolama:** Etkinlik verilerini **PostgreSQL veritabanında** güvenli ve ölçeklenebilir bir şekilde depolar.
* **Kullanıcı Dostu Web Arayüzü:** Çekilen etkinlikleri kategoriye göre gruplandırılmış, görselliği ön planda tutan modern ve **tam responsive bir arayüzde** sunar.
* **Tek Tıkla Güncelleme:** Web arayüzü üzerinden "Verileri Güncelle" butonu ile en güncel etkinlikleri anında çekme imkanı.
* **Durum Takibi:** Etkinliklerin son güncelleme zamanını ve toplam etkinlik sayısını gösterir.
* **Üretim Ortamı İçin Yapılandırma:** **Docker, Nginx ve uWSGI** entegrasyonu ile hızlı ve güvenilir dağıtım.

## 🛠️ Teknolojiler

* **Python:** Backend scraping mantığı ve Flask uygulaması için ana dil.
* **Flask:** Hafif ve esnek bir Python web çatısı ile web arayüzünü oluşturur.
* **PostgreSQL:** Etkinlik verilerini depolamak için kullanılan ilişkisel veritabanı.
* **SQLAlchemy:** Flask uygulamasını PostgreSQL veritabanına bağlamak için kullanılan ORM (Object Relational Mapper).
* **Selenium:** Dinamik web sitelerinden veri çekmek için kullanılır.
* **BeautifulSoup4:** Çekilen HTML içeriğini ayrıştırmak için kullanılır.
* **WebDriver-Manager:** Selenium WebDriver'ları otomatik olarak yönetir.
* **Docker:** Uygulamanın ve veritabanının kapsayıcılı (containerized) ortamda çalışması için.
* **Nginx:** Web sunucusu ve ters proxy olarak görev yapar, statik dosyaları servis eder ve Flask uygulamasına gelen istekleri yönlendirir.
* **uWSGI:** Flask uygulamasını Nginx ile entegre etmek için kullanılan bir uygulama sunucusu arayüzü.
* **HTML/CSS/JavaScript:** Web arayüzünün frontend tasarımı ve etkileşimi için.

## 🚀 Kurulum ve Çalıştırma

Projeyi yerel makinenizde kurmak ve çalıştırmak için veya üretim ortamında dağıtmak için aşağıdaki adımları izleyin.

**Önemli Not:** Bu depoda, platformların Hizmet Şartları ve etik nedenlerle web scraper kodları (`scrapers/` dizini) bulunmamaktadır. Eğer scraper'ları çalıştırmak istiyorsanız, bu modülleri kendi özel deponuzdan veya yerel olarak projenize eklemeniz gerekmektedir. 

### Önkoşullar

* [Git](https://git-scm.com/downloads) (Repoyu klonlamak için)
* [Docker](https://www.docker.com/get-started/) ve [Docker Compose](https://docs.docker.com/compose/install/)
* [Google Chrome](https://www.google.com/chrome/) (Selenium için tarayıcı - **sadece yerel geliştirme için gerekli, Docker'da genellikle tarayıcı kapsayıcıda yüklüdür**)

### Adımlar

1.  **Repoyu Klonlayın:**
    ```bash
    git clone https://github.com/Metrohan/TechEventRadar.git
    cd TechEventRadar
    ```

2.  **Docker Ortamını Başlatın (Uygulama ve PostgreSQL):**
    ```bash
    docker-compose up --build -d
    ```
    Bu komut, `Dockerfile`'ı kullanarak Flask uygulamasını oluşturacak, `docker-compose.yml`'deki servisleri (Flask uygulaması ve PostgreSQL) başlatacak ve arka planda çalıştıracaktır.

3.  **Veritabanı Tablolarını Oluşturun (İlk Kez Çalıştırıldığında):**
    Flask uygulamanız ilk kez ayağa kalktığında otomatik olarak tabloları oluşturacaktır (`db.create_all()` sayesinde).

4.  **Scraper'ları Çalıştırın ve Verileri Çekin (İlk Kez Veritabanını Doldurmak veya Manuel Güncelleme İçin):**
    Flask uygulamasının kapsayıcısına bağlanarak scraper'ları çalıştırın:

    ```bash
    docker-compose exec app python main.py
    ```


    Bu komut, tanımlı tüm kaynaklardan etkinlik verilerini çekecek ve PostgreSQL veritabanına kaydedecektir.

5.  **Nginx Kurulumu (Üretim Ortamı İçin):**
    Üretim ortamında `eventradar.dev` gibi bir alan adı üzerinden erişim sağlamak için Nginx yapılandırması gereklidir.
    * `/etc/nginx/sites-available/` dizininde `eventradar.dev` adında bir Nginx yapılandırma dosyası oluşturun (veya düzenleyin).
    * İçine aşağıdaki örnek yapılandırmayı yapıştırın ve **kendi alan adınız ile proje yolunuzu (`/home/username/TechEventRadar/` gibi)** güncelleyin.

    ```nginx
    server {
        listen 80;
        server_name eventradar.dev www.eventradar.dev; # Kendi alan adlarını buraya ekle

        location / {
            return 301 https://$host$request_uri; # HTTP isteklerini HTTPS'ye yönlendir
        }
    }

    server {
        listen 443 ssl;
        server_name eventradar.dev www.eventradar.dev; # Kendi alan adlarını buraya ekle

        ssl_certificate /etc/letsencrypt/live/eventradar.dev/fullchain.pem; # Sertifika yolu (Let's Encrypt sonrası)
        ssl_key /etc/letsencrypt/live/eventradar.dev/privkey.pem;         # Anahtar yolu (Let's Encrypt sonrası)

        include /etc/letsencrypt/options-ssl-nginx.conf;
        ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

        root /home/username/TechEventRadar/; # Flask projenin ANA dizini (app.py, static, templates'ın olduğu dizin)

        location / {
            try_files $uri @app;
        }

        location @app {
            include uwsgi_params;
            uwsgi_pass unix:/home/username/TechEventRadar/eventradar.sock; # uWSGI socket yolunu kontrol et
        }

        location /static/ {
            root /home/username/TechEventRadar/; # Burası /home/username/TechEventRadar/static/ olmalı
            expires 30d;
            add_header Cache-Control "public";
            try_files $uri =404;
        }
    }
    ```
    * Bu yapılandırma dosyasına sembolik link oluşturun:
        ```bash
        sudo ln -s /etc/nginx/sites-available/eventradar.dev /etc/nginx/sites-enabled/
        ```
    * Nginx'in statik dosyalara ve ana dizine erişebilmesi için gerekli izinleri verin:
        ```bash
        sudo chmod o+x /home/username/
        sudo find /home/username/TechEventRadar/static -type d -exec chmod 755 {} +
        sudo find /home/username/TechEventRadar/static -type f -exec chmod 644 {} +
        ```
    * Nginx yapılandırmasını test edin ve yeniden yükleyin:
        ```bash
        sudo nginx -t
        sudo systemctl reload nginx
        ```

6.  **Tarayıcınızda Açın:**
    Nginx ve Docker Compose düzgün çalıştığında, tarayıcınızda yapılandırdığınız alan adı (örn: `https://eventradar.dev/`) üzerinden uygulamaya erişebilirsiniz. Etkinlikleri görüntüleyebilir ve "Verileri Güncelle" butonuna tıklayarak verileri web arayüzünden güncelleyebilirsiniz.

## 📂 Proje Yapısı

```bash
TechEventRadar/
├── main.py                 # Scraper'ları çalıştıran ana dosya (PostgreSQL'e yazar)
├── app.py                  # Flask web uygulaması (PostgreSQL'den okur)
├── docker-compose.yml      # Docker Compose yapılandırması (Uygulama ve PostgreSQL)
├── Dockerfile              # Flask uygulamasının Docker imajı tanımı
├── run_daily_scrape.py     # Otomatik günlük veri çekme scripti (cronjob için ideal)
├── scrapers/               # Etik sebepler gereği sizin yazmanız gerekmekte
├── templates/              # HTML şablonlarının bulunduğu dizin
│   └── index.html          # Ana sayfa HTML şablonu
└── static/                 # CSS, JavaScript, resimler gibi statik dosyalar
    ├── css/                # CSS dosyaları
    │   └── style.css
    └── images/             # Resim dosyaları
        └── default-event.jpg # veya placeholder-image.jpeg
```

🤝 Katkıda Bulunma

Projeye katkıda bulunmanızdan mutluluk duyarım! Nasıl katkıda bulunabileceğinizi öğrenmek için lütfen Katkıda Bulunma Rehberi dosyasını inceleyin.

📜 Lisans

Bu proje MIT Lisansı altında lisanslanmıştır. Daha fazla bilgi için LICENSE dosyasına bakın.

```
AdminTechEventRadar
├─ .env
├─ app.py
├─ config.py
├─ CONTRIBUTING.md
├─ docker-compose.yml
├─ Dockerfile
├─ extensions.py
├─ instance
│  └─ events.db
├─ LICENSE
├─ models
│  ├─ announcement.py
│  ├─ event.py
│  ├─ event_request.py
│  ├─ pending_event.py
│  ├─ similar_event_pair.py
│  ├─ suggestion.py
│  └─ __init__.py
├─ README.md
├─ requirements.txt
├─ routes
│  ├─ admin.py
│  ├─ announcements.py
│  ├─ api.py
│  ├─ events.py
│  ├─ pending.py
│  ├─ public.py
│  ├─ requests.py
│  ├─ suggestions.py
│  └─ __init__.py
├─ run_daily_scrape.py
├─ scrapers
│  ├─ anbean_scraper.py
│  ├─ cs_scraper.py
│  ├─ kodluyoruz_scraper.py
│  ├─ techcareer_scraper.py
│  ├─ youthall_scraper.py
│  └─ __pycache__
│     ├─ anbean_scraper.cpython-311.pyc
│     ├─ anbean_scraper.cpython-39.pyc
│     ├─ cs_scraper.cpython-311.pyc
│     ├─ cs_scraper.cpython-39.pyc
│     ├─ kodluyoruz_scraper.cpython-311.pyc
│     ├─ kodluyoruz_scraper.cpython-39.pyc
│     ├─ techcareer_scraper.cpython-311.pyc
│     ├─ techcareer_scraper.cpython-39.pyc
│     ├─ youthall_scraper.cpython-311.pyc
│     ├─ youthall_scraper.cpython-39.pyc
│     └─ __init__.cpython-311.pyc
├─ services
│  └─ scraper_service.py
├─ static
│  ├─ css
│  │  └─ style.css
│  ├─ images
│  │  ├─ coffee.svg
│  │  ├─ favicon.ico
│  │  ├─ github-mark-white.png
│  │  ├─ placeholder-image-colored.jpeg
│  │  └─ techeventradar_logo.png
│  └─ js
├─ templates
│  ├─ add_announcement.html
│  ├─ add_event.html
│  ├─ admin_login.html
│  ├─ dashboard.html
│  ├─ edit_event.html
│  ├─ etkinlik_talep.html
│  ├─ index.html
│  ├─ oneri_sikayet.html
│  ├─ requests.html
│  └─ suggestion.html
├─ utils
│  ├─ auth.py
│  ├─ filters.py
│  └─ __init__.py
├─ venv
│  ├─ Include
│  │  └─ site
│  │     └─ python3.11
│  │        └─ greenlet
│  │           └─ greenlet.h
│  ├─ Lib
│  │  └─ site-packages
│  │     ├─ attr
│  │     │  ├─ converters.py
│  │     │  ├─ converters.pyi
│  │     │  ├─ exceptions.py
│  │     │  ├─ exceptions.pyi
│  │     │  ├─ filters.py
│  │     │  ├─ filters.pyi
│  │     │  ├─ py.typed
│  │     │  ├─ setters.py
│  │     │  ├─ setters.pyi
│  │     │  ├─ validators.py
│  │     │  ├─ validators.pyi
│  │     │  ├─ _cmp.py
│  │     │  ├─ _cmp.pyi
│  │     │  ├─ _compat.py
│  │     │  ├─ _config.py
│  │     │  ├─ _funcs.py
│  │     │  ├─ _make.py
│  │     │  ├─ _next_gen.py
│  │     │  ├─ _typing_compat.pyi
│  │     │  ├─ _version_info.py
│  │     │  ├─ _version_info.pyi
│  │     │  ├─ __init__.py
│  │     │  ├─ __init__.pyi
│  │     │  └─ __pycache__
│  │     │     ├─ converters.cpython-311.pyc
│  │     │     ├─ exceptions.cpython-311.pyc
│  │     │     ├─ filters.cpython-311.pyc
│  │     │     ├─ setters.cpython-311.pyc
│  │     │     ├─ validators.cpython-311.pyc
│  │     │     ├─ _cmp.cpython-311.pyc
│  │     │     ├─ _compat.cpython-311.pyc
│  │     │     ├─ _config.cpython-311.pyc
│  │     │     ├─ _funcs.cpython-311.pyc
│  │     │     ├─ _make.cpython-311.pyc
│  │     │     ├─ _next_gen.cpython-311.pyc
│  │     │     ├─ _version_info.cpython-311.pyc
│  │     │     └─ __init__.cpython-311.pyc
│  │     ├─ attrs
│  │     │  ├─ converters.py
│  │     │  ├─ exceptions.py
│  │     │  ├─ filters.py
│  │     │  ├─ py.typed
│  │     │  ├─ setters.py
│  │     │  ├─ validators.py
│  │     │  ├─ __init__.py
│  │     │  ├─ __init__.pyi
│  │     │  └─ __pycache__
│  │     │     ├─ converters.cpython-311.pyc
│  │     │     ├─ exceptions.cpython-311.pyc
│  │     │     ├─ filters.cpython-311.pyc
│  │     │     ├─ setters.cpython-311.pyc
│  │     │     ├─ validators.cpython-311.pyc
│  │     │     └─ __init__.cpython-311.pyc
│  │     ├─ attrs-25.3.0.dist-info
│  │     │  ├─ INSTALLER
│  │     │  ├─ licenses
│  │     │  │  └─ LICENSE
│  │     │  ├─ METADATA
│  │     │  ├─ RECORD
│  │     │  └─ WHEEL
│  │     ├─ beautifulsoup4-4.13.4.dist-info
│  │     │  ├─ INSTALLER
│  │     │  ├─ licenses
│  │     │  │  ├─ AUTHORS
│  │     │  │  └─ LICENSE
│  │     │  ├─ METADATA
│  │     │  ├─ RECORD
│  │     │  ├─ REQUESTED
│  │     │  └─ WHEEL
│  │     ├─ blinker
│  │     │  ├─ base.py
│  │     │  ├─ py.typed
│  │     │  ├─ _utilities.py
│  │     │  ├─ __init__.py
│  │     │  └─ __pycache__
│  │     │     ├─ base.cpython-311.pyc
│  │     │     ├─ _utilities.cpython-311.pyc
│  │     │     └─ __init__.cpython-311.pyc
│  │     ├─ blinker-1.9.0.dist-info
│  │     │  ├─ INSTALLER
│  │     │  ├─ LICENSE.txt
│  │     │  ├─ METADATA
│  │     │  ├─ RECORD
│  │     │  └─ WHEEL
│  │     ├─ bs4
│  │     │  ├─ builder
│  │     │  │  ├─ _html5lib.py
│  │     │  │  ├─ _htmlparser.py
│  │     │  │  ├─ _lxml.py
│  │     │  │  ├─ __init__.py
│  │     │  │  └─ __pycache__
│  │     │  │     ├─ _html5lib.cpython-311.pyc
│  │     │  │     ├─ _htmlparser.cpython-311.pyc
│  │     │  │     ├─ _lxml.cpython-311.pyc
│  │     │  │     └─ __init__.cpython-311.pyc
│  │     │  ├─ css.py
│  │     │  ├─ dammit.py
│  │     │  ├─ diagnose.py
│  │     │  ├─ element.py
│  │     │  ├─ exceptions.py
│  │     │  ├─ filter.py
│  │     │  ├─ formatter.py
│  │     │  ├─ py.typed
│  │     │  ├─ tests
│  │     │  │  ├─ fuzz
│  │     │  │  │  ├─ clusterfuzz-testcase-minimized-bs4_fuzzer-4670634698080256.testcase
│  │     │  │  │  ├─ clusterfuzz-testcase-minimized-bs4_fuzzer-4818336571064320.testcase
│  │     │  │  │  ├─ clusterfuzz-testcase-minimized-bs4_fuzzer-4999465949331456.testcase
│  │     │  │  │  ├─ clusterfuzz-testcase-minimized-bs4_fuzzer-5000587759190016.testcase
│  │     │  │  │  ├─ clusterfuzz-testcase-minimized-bs4_fuzzer-5167584867909632.testcase
│  │     │  │  │  ├─ clusterfuzz-testcase-minimized-bs4_fuzzer-5270998950477824.testcase
│  │     │  │  │  ├─ clusterfuzz-testcase-minimized-bs4_fuzzer-5375146639360000.testcase
│  │     │  │  │  ├─ clusterfuzz-testcase-minimized-bs4_fuzzer-5492400320282624.testcase
│  │     │  │  │  ├─ clusterfuzz-testcase-minimized-bs4_fuzzer-5703933063462912.testcase
│  │     │  │  │  ├─ clusterfuzz-testcase-minimized-bs4_fuzzer-5843991618256896.testcase
│  │     │  │  │  ├─ clusterfuzz-testcase-minimized-bs4_fuzzer-5984173902397440.testcase
│  │     │  │  │  ├─ clusterfuzz-testcase-minimized-bs4_fuzzer-6124268085182464.testcase
│  │     │  │  │  ├─ clusterfuzz-testcase-minimized-bs4_fuzzer-6241471367348224.testcase
│  │     │  │  │  ├─ clusterfuzz-testcase-minimized-bs4_fuzzer-6306874195312640.testcase
│  │     │  │  │  ├─ clusterfuzz-testcase-minimized-bs4_fuzzer-6450958476902400.testcase
│  │     │  │  │  ├─ clusterfuzz-testcase-minimized-bs4_fuzzer-6600557255327744.testcase
│  │     │  │  │  ├─ crash-0d306a50c8ed8bcd0785b67000fcd5dea1d33f08.testcase
│  │     │  │  │  └─ crash-ffbdfa8a2b26f13537b68d3794b0478a4090ee4a.testcase
│  │     │  │  ├─ test_builder.py
│  │     │  │  ├─ test_builder_registry.py
│  │     │  │  ├─ test_css.py
│  │     │  │  ├─ test_dammit.py
│  │     │  │  ├─ test_element.py
│  │     │  │  ├─ test_filter.py
│  │     │  │  ├─ test_formatter.py
│  │     │  │  ├─ test_fuzz.py
│  │     │  │  ├─ test_html5lib.py
│  │     │  │  ├─ test_htmlparser.py
│  │     │  │  ├─ test_lxml.py
│  │     │  │  ├─ test_navigablestring.py
│  │     │  │  ├─ test_pageelement.py
│  │     │  │  ├─ test_soup.py
│  │     │  │  ├─ test_tag.py
│  │     │  │  ├─ test_tree.py
│  │     │  │  ├─ __init__.py
│  │     │  │  └─ __pycache__
│  │     │  │     ├─ test_builder.cpython-311.pyc
│  │     │  │     ├─ test_builder_registry.cpython-311.pyc
│  │     │  │     ├─ test_css.cpython-311.pyc
│  │     │  │     ├─ test_dammit.cpython-311.pyc
│  │     │  │     ├─ test_element.cpython-311.pyc
│  │     │  │     ├─ test_filter.cpython-311.pyc
│  │     │  │     ├─ test_formatter.cpython-311.pyc
│  │     │  │     ├─ test_fuzz.cpython-311.pyc
│  │     │  │     ├─ test_html5lib.cpython-311.pyc
│  │     │  │     ├─ test_htmlparser.cpython-311.pyc
│  │     │  │     ├─ test_lxml.cpython-311.pyc
│  │     │  │     ├─ test_navigablestring.cpython-311.pyc
│  │     │  │     ├─ test_pageelement.cpython-311.pyc
│  │     │  │     ├─ test_soup.cpython-311.pyc
│  │     │  │     ├─ test_tag.cpython-311.pyc
│  │     │  │     ├─ test_tree.cpython-311.pyc
│  │     │  │     └─ __init__.cpython-311.pyc
│  │     │  ├─ _deprecation.py
│  │     │  ├─ _typing.py
│  │     │  ├─ _warnings.py
│  │     │  ├─ __init__.py
│  │     │  └─ __pycache__
│  │     │     ├─ css.cpython-311.pyc
│  │     │     ├─ dammit.cpython-311.pyc
│  │     │     ├─ diagnose.cpython-311.pyc
│  │     │     ├─ element.cpython-311.pyc
│  │     │     ├─ exceptions.cpython-311.pyc
│  │     │     ├─ filter.cpython-311.pyc
│  │     │     ├─ formatter.cpython-311.pyc
│  │     │     ├─ _deprecation.cpython-311.pyc
│  │     │     ├─ _typing.cpython-311.pyc
│  │     │     ├─ _warnings.cpython-311.pyc
│  │     │     └─ __init__.cpython-311.pyc
│  │     ├─ certifi
│  │     │  ├─ cacert.pem
│  │     │  ├─ core.py
│  │     │  ├─ py.typed
│  │     │  ├─ __init__.py
│  │     │  ├─ __main__.py
│  │     │  └─ __pycache__
│  │     │     ├─ core.cpython-311.pyc
│  │     │     ├─ __init__.cpython-311.pyc
│  │     │     └─ __main__.cpython-311.pyc
│  │     ├─ certifi-2025.7.14.dist-info
│  │     │  ├─ INSTALLER
│  │     │  ├─ licenses
│  │     │  │  └─ LICENSE
│  │     │  ├─ METADATA
│  │     │  ├─ RECORD
│  │     │  ├─ top_level.txt
│  │     │  └─ WHEEL
│  │     ├─ cffi
│  │     │  ├─ api.py
│  │     │  ├─ backend_ctypes.py
│  │     │  ├─ cffi_opcode.py
│  │     │  ├─ commontypes.py
│  │     │  ├─ cparser.py
│  │     │  ├─ error.py
│  │     │  ├─ ffiplatform.py
│  │     │  ├─ lock.py
│  │     │  ├─ model.py
│  │     │  ├─ parse_c_type.h
│  │     │  ├─ pkgconfig.py
│  │     │  ├─ recompiler.py
│  │     │  ├─ setuptools_ext.py
│  │     │  ├─ vengine_cpy.py
│  │     │  ├─ vengine_gen.py
│  │     │  ├─ verifier.py
│  │     │  ├─ _cffi_errors.h
│  │     │  ├─ _cffi_include.h
│  │     │  ├─ _embedding.h
│  │     │  ├─ _imp_emulation.py
│  │     │  ├─ _shimmed_dist_utils.py
│  │     │  ├─ __init__.py
│  │     │  └─ __pycache__
│  │     │     ├─ api.cpython-311.pyc
│  │     │     ├─ backend_ctypes.cpython-311.pyc
│  │     │     ├─ cffi_opcode.cpython-311.pyc
│  │     │     ├─ commontypes.cpython-311.pyc
│  │     │     ├─ cparser.cpython-311.pyc
│  │     │     ├─ error.cpython-311.pyc
│  │     │     ├─ ffiplatform.cpython-311.pyc
│  │     │     ├─ lock.cpython-311.pyc
│  │     │     ├─ model.cpython-311.pyc
│  │     │     ├─ pkgconfig.cpython-311.pyc
│  │     │     ├─ recompiler.cpython-311.pyc
│  │     │     ├─ setuptools_ext.cpython-311.pyc
│  │     │     ├─ vengine_cpy.cpython-311.pyc
│  │     │     ├─ vengine_gen.cpython-311.pyc
│  │     │     ├─ verifier.cpython-311.pyc
│  │     │     ├─ _imp_emulation.cpython-311.pyc
│  │     │     ├─ _shimmed_dist_utils.cpython-311.pyc
│  │     │     └─ __init__.cpython-311.pyc
│  │     ├─ cffi-1.17.1.dist-info
│  │     │  ├─ entry_points.txt
│  │     │  ├─ INSTALLER
│  │     │  ├─ LICENSE
│  │     │  ├─ METADATA
│  │     │  ├─ RECORD
│  │     │  ├─ top_level.txt
│  │     │  └─ WHEEL
│  │     ├─ charset_normalizer
│  │     │  ├─ api.py
│  │     │  ├─ cd.py
│  │     │  ├─ cli
│  │     │  │  ├─ __init__.py
│  │     │  │  ├─ __main__.py
│  │     │  │  └─ __pycache__
│  │     │  │     ├─ __init__.cpython-311.pyc
│  │     │  │     └─ __main__.cpython-311.pyc
│  │     │  ├─ constant.py
│  │     │  ├─ legacy.py
│  │     │  ├─ md.cp311-win_amd64.pyd
│  │     │  ├─ md.py
│  │     │  ├─ md__mypyc.cp311-win_amd64.pyd
│  │     │  ├─ models.py
│  │     │  ├─ py.typed
│  │     │  ├─ utils.py
│  │     │  ├─ version.py
│  │     │  ├─ __init__.py
│  │     │  ├─ __main__.py
│  │     │  └─ __pycache__
│  │     │     ├─ api.cpython-311.pyc
│  │     │     ├─ cd.cpython-311.pyc
│  │     │     ├─ constant.cpython-311.pyc
│  │     │     ├─ legacy.cpython-311.pyc
│  │     │     ├─ md.cpython-311.pyc
│  │     │     ├─ models.cpython-311.pyc
│  │     │     ├─ utils.cpython-311.pyc
│  │     │     ├─ version.cpython-311.pyc
│  │     │     ├─ __init__.cpython-311.pyc
│  │     │     └─ __main__.cpython-311.pyc
│  │     ├─ charset_normalizer-3.4.2.dist-info
│  │     │  ├─ entry_points.txt
│  │     │  ├─ INSTALLER
│  │     │  ├─ licenses
│  │     │  │  └─ LICENSE
│  │     │  ├─ METADATA
│  │     │  ├─ RECORD
│  │     │  ├─ top_level.txt
│  │     │  └─ WHEEL
│  │     ├─ click
│  │     │  ├─ core.py
│  │     │  ├─ decorators.py
│  │     │  ├─ exceptions.py
│  │     │  ├─ formatting.py
│  │     │  ├─ globals.py
│  │     │  ├─ parser.py
│  │     │  ├─ py.typed
│  │     │  ├─ shell_completion.py
│  │     │  ├─ termui.py
│  │     │  ├─ testing.py
│  │     │  ├─ types.py
│  │     │  ├─ utils.py
│  │     │  ├─ _compat.py
│  │     │  ├─ _termui_impl.py
│  │     │  ├─ _textwrap.py
│  │     │  ├─ _winconsole.py
│  │     │  ├─ __init__.py
│  │     │  └─ __pycache__
│  │     │     ├─ core.cpython-311.pyc
│  │     │     ├─ decorators.cpython-311.pyc
│  │     │     ├─ exceptions.cpython-311.pyc
│  │     │     ├─ formatting.cpython-311.pyc
│  │     │     ├─ globals.cpython-311.pyc
│  │     │     ├─ parser.cpython-311.pyc
│  │     │     ├─ shell_completion.cpython-311.pyc
│  │     │     ├─ termui.cpython-311.pyc
│  │     │     ├─ testing.cpython-311.pyc
│  │     │     ├─ types.cpython-311.pyc
│  │     │     ├─ utils.cpython-311.pyc
│  │     │     ├─ _compat.cpython-311.pyc
│  │     │     ├─ _termui_impl.cpython-311.pyc
│  │     │     ├─ _textwrap.cpython-311.pyc
│  │     │     ├─ _winconsole.cpython-311.pyc
│  │     │     └─ __init__.cpython-311.pyc
│  │     ├─ click-8.2.1.dist-info
│  │     │  ├─ INSTALLER
│  │     │  ├─ licenses
│  │     │  │  └─ LICENSE.txt
│  │     │  ├─ METADATA
│  │     │  ├─ RECORD
│  │     │  └─ WHEEL
│  │     ├─ colorama
│  │     │  ├─ ansi.py
│  │     │  ├─ ansitowin32.py
│  │     │  ├─ initialise.py
│  │     │  ├─ tests
│  │     │  │  ├─ ansitowin32_test.py
│  │     │  │  ├─ ansi_test.py
│  │     │  │  ├─ initialise_test.py
│  │     │  │  ├─ isatty_test.py
│  │     │  │  ├─ utils.py
│  │     │  │  ├─ winterm_test.py
│  │     │  │  ├─ __init__.py
│  │     │  │  └─ __pycache__
│  │     │  │     ├─ ansitowin32_test.cpython-311.pyc
│  │     │  │     ├─ ansi_test.cpython-311.pyc
│  │     │  │     ├─ initialise_test.cpython-311.pyc
│  │     │  │     ├─ isatty_test.cpython-311.pyc
│  │     │  │     ├─ utils.cpython-311.pyc
│  │     │  │     ├─ winterm_test.cpython-311.pyc
│  │     │  │     └─ __init__.cpython-311.pyc
│  │     │  ├─ win32.py
│  │     │  ├─ winterm.py
│  │     │  ├─ __init__.py
│  │     │  └─ __pycache__
│  │     │     ├─ ansi.cpython-311.pyc
│  │     │     ├─ ansitowin32.cpython-311.pyc
│  │     │     ├─ initialise.cpython-311.pyc
│  │     │     ├─ win32.cpython-311.pyc
│  │     │     ├─ winterm.cpython-311.pyc
│  │     │     └─ __init__.cpython-311.pyc
│  │     ├─ colorama-0.4.6.dist-info
│  │     │  ├─ INSTALLER
│  │     │  ├─ licenses
│  │     │  │  └─ LICENSE.txt
│  │     │  ├─ METADATA
│  │     │  ├─ RECORD
│  │     │  └─ WHEEL
│  │     ├─ distutils-precedence.pth
│  │     ├─ dotenv
│  │     │  ├─ cli.py
│  │     │  ├─ ipython.py
│  │     │  ├─ main.py
│  │     │  ├─ parser.py
│  │     │  ├─ py.typed
│  │     │  ├─ variables.py
│  │     │  ├─ version.py
│  │     │  ├─ __init__.py
│  │     │  ├─ __main__.py
│  │     │  └─ __pycache__
│  │     │     ├─ cli.cpython-311.pyc
│  │     │     ├─ ipython.cpython-311.pyc
│  │     │     ├─ main.cpython-311.pyc
│  │     │     ├─ parser.cpython-311.pyc
│  │     │     ├─ variables.cpython-311.pyc
│  │     │     ├─ version.cpython-311.pyc
│  │     │     ├─ __init__.cpython-311.pyc
│  │     │     └─ __main__.cpython-311.pyc
│  │     ├─ flask
│  │     │  ├─ app.py
│  │     │  ├─ blueprints.py
│  │     │  ├─ cli.py
│  │     │  ├─ config.py
│  │     │  ├─ ctx.py
│  │     │  ├─ debughelpers.py
│  │     │  ├─ globals.py
│  │     │  ├─ helpers.py
│  │     │  ├─ json
│  │     │  │  ├─ provider.py
│  │     │  │  ├─ tag.py
│  │     │  │  ├─ __init__.py
│  │     │  │  └─ __pycache__
│  │     │  │     ├─ provider.cpython-311.pyc
│  │     │  │     ├─ tag.cpython-311.pyc
│  │     │  │     └─ __init__.cpython-311.pyc
│  │     │  ├─ logging.py
│  │     │  ├─ py.typed
│  │     │  ├─ sansio
│  │     │  │  ├─ app.py
│  │     │  │  ├─ blueprints.py
│  │     │  │  ├─ README.md
│  │     │  │  ├─ scaffold.py
│  │     │  │  └─ __pycache__
│  │     │  │     ├─ app.cpython-311.pyc
│  │     │  │     ├─ blueprints.cpython-311.pyc
│  │     │  │     └─ scaffold.cpython-311.pyc
│  │     │  ├─ sessions.py
│  │     │  ├─ signals.py
│  │     │  ├─ templating.py
│  │     │  ├─ testing.py
│  │     │  ├─ typing.py
│  │     │  ├─ views.py
│  │     │  ├─ wrappers.py
│  │     │  ├─ __init__.py
│  │     │  ├─ __main__.py
│  │     │  └─ __pycache__
│  │     │     ├─ app.cpython-311.pyc
│  │     │     ├─ blueprints.cpython-311.pyc
│  │     │     ├─ cli.cpython-311.pyc
│  │     │     ├─ config.cpython-311.pyc
│  │     │     ├─ ctx.cpython-311.pyc
│  │     │     ├─ debughelpers.cpython-311.pyc
│  │     │     ├─ globals.cpython-311.pyc
│  │     │     ├─ helpers.cpython-311.pyc
│  │     │     ├─ logging.cpython-311.pyc
│  │     │     ├─ sessions.cpython-311.pyc
│  │     │     ├─ signals.cpython-311.pyc
│  │     │     ├─ templating.cpython-311.pyc
│  │     │     ├─ testing.cpython-311.pyc
│  │     │     ├─ typing.cpython-311.pyc
│  │     │     ├─ views.cpython-311.pyc
│  │     │     ├─ wrappers.cpython-311.pyc
│  │     │     ├─ __init__.cpython-311.pyc
│  │     │     └─ __main__.cpython-311.pyc
│  │     ├─ flask-3.1.1.dist-info
│  │     │  ├─ entry_points.txt
│  │     │  ├─ INSTALLER
│  │     │  ├─ licenses
│  │     │  │  └─ LICENSE.txt
│  │     │  ├─ METADATA
│  │     │  ├─ RECORD
│  │     │  ├─ REQUESTED
│  │     │  └─ WHEEL
│  │     ├─ flask_sqlalchemy
│  │     │  ├─ cli.py
│  │     │  ├─ extension.py
│  │     │  ├─ model.py
│  │     │  ├─ pagination.py
│  │     │  ├─ py.typed
│  │     │  ├─ query.py
│  │     │  ├─ record_queries.py
│  │     │  ├─ session.py
│  │     │  ├─ table.py
│  │     │  ├─ track_modifications.py
│  │     │  ├─ __init__.py
│  │     │  └─ __pycache__
│  │     │     ├─ cli.cpython-311.pyc
│  │     │     ├─ extension.cpython-311.pyc
│  │     │     ├─ model.cpython-311.pyc
│  │     │     ├─ pagination.cpython-311.pyc
│  │     │     ├─ query.cpython-311.pyc
│  │     │     ├─ record_queries.cpython-311.pyc
│  │     │     ├─ session.cpython-311.pyc
│  │     │     ├─ table.cpython-311.pyc
│  │     │     ├─ track_modifications.cpython-311.pyc
│  │     │     └─ __init__.cpython-311.pyc
│  │     ├─ flask_sqlalchemy-3.1.1.dist-info
│  │     │  ├─ INSTALLER
│  │     │  ├─ LICENSE.rst
│  │     │  ├─ METADATA
│  │     │  ├─ RECORD
│  │     │  ├─ REQUESTED
│  │     │  └─ WHEEL
│  │     ├─ greenlet
│  │     │  ├─ CObjects.cpp
│  │     │  ├─ greenlet.cpp
│  │     │  ├─ greenlet.h
│  │     │  ├─ greenlet_allocator.hpp
│  │     │  ├─ greenlet_compiler_compat.hpp
│  │     │  ├─ greenlet_cpython_compat.hpp
│  │     │  ├─ greenlet_exceptions.hpp
│  │     │  ├─ greenlet_internal.hpp
│  │     │  ├─ greenlet_msvc_compat.hpp
│  │     │  ├─ greenlet_refs.hpp
│  │     │  ├─ greenlet_slp_switch.hpp
│  │     │  ├─ greenlet_thread_support.hpp
│  │     │  ├─ platform
│  │     │  │  ├─ setup_switch_x64_masm.cmd
│  │     │  │  ├─ switch_aarch64_gcc.h
│  │     │  │  ├─ switch_alpha_unix.h
│  │     │  │  ├─ switch_amd64_unix.h
│  │     │  │  ├─ switch_arm32_gcc.h
│  │     │  │  ├─ switch_arm32_ios.h
│  │     │  │  ├─ switch_arm64_masm.asm
│  │     │  │  ├─ switch_arm64_masm.obj
│  │     │  │  ├─ switch_arm64_msvc.h
│  │     │  │  ├─ switch_csky_gcc.h
│  │     │  │  ├─ switch_loongarch64_linux.h
│  │     │  │  ├─ switch_m68k_gcc.h
│  │     │  │  ├─ switch_mips_unix.h
│  │     │  │  ├─ switch_ppc64_aix.h
│  │     │  │  ├─ switch_ppc64_linux.h
│  │     │  │  ├─ switch_ppc_aix.h
│  │     │  │  ├─ switch_ppc_linux.h
│  │     │  │  ├─ switch_ppc_macosx.h
│  │     │  │  ├─ switch_ppc_unix.h
│  │     │  │  ├─ switch_riscv_unix.h
│  │     │  │  ├─ switch_s390_unix.h
│  │     │  │  ├─ switch_sh_gcc.h
│  │     │  │  ├─ switch_sparc_sun_gcc.h
│  │     │  │  ├─ switch_x32_unix.h
│  │     │  │  ├─ switch_x64_masm.asm
│  │     │  │  ├─ switch_x64_masm.obj
│  │     │  │  ├─ switch_x64_msvc.h
│  │     │  │  ├─ switch_x86_msvc.h
│  │     │  │  ├─ switch_x86_unix.h
│  │     │  │  ├─ __init__.py
│  │     │  │  └─ __pycache__
│  │     │  │     └─ __init__.cpython-311.pyc
│  │     │  ├─ PyGreenlet.cpp
│  │     │  ├─ PyGreenlet.hpp
│  │     │  ├─ PyGreenletUnswitchable.cpp
│  │     │  ├─ PyModule.cpp
│  │     │  ├─ slp_platformselect.h
│  │     │  ├─ TBrokenGreenlet.cpp
│  │     │  ├─ tests
│  │     │  │  ├─ fail_clearing_run_switches.py
│  │     │  │  ├─ fail_cpp_exception.py
│  │     │  │  ├─ fail_initialstub_already_started.py
│  │     │  │  ├─ fail_slp_switch.py
│  │     │  │  ├─ fail_switch_three_greenlets.py
│  │     │  │  ├─ fail_switch_three_greenlets2.py
│  │     │  │  ├─ fail_switch_two_greenlets.py
│  │     │  │  ├─ leakcheck.py
│  │     │  │  ├─ test_contextvars.py
│  │     │  │  ├─ test_cpp.py
│  │     │  │  ├─ test_extension_interface.py
│  │     │  │  ├─ test_gc.py
│  │     │  │  ├─ test_generator.py
│  │     │  │  ├─ test_generator_nested.py
│  │     │  │  ├─ test_greenlet.py
│  │     │  │  ├─ test_greenlet_trash.py
│  │     │  │  ├─ test_leaks.py
│  │     │  │  ├─ test_stack_saved.py
│  │     │  │  ├─ test_throw.py
│  │     │  │  ├─ test_tracing.py
│  │     │  │  ├─ test_version.py
│  │     │  │  ├─ test_weakref.py
│  │     │  │  ├─ _test_extension.c
│  │     │  │  ├─ _test_extension.cp311-win_amd64.pyd
│  │     │  │  ├─ _test_extension_cpp.cp311-win_amd64.pyd
│  │     │  │  ├─ _test_extension_cpp.cpp
│  │     │  │  ├─ __init__.py
│  │     │  │  └─ __pycache__
│  │     │  │     ├─ fail_clearing_run_switches.cpython-311.pyc
│  │     │  │     ├─ fail_cpp_exception.cpython-311.pyc
│  │     │  │     ├─ fail_initialstub_already_started.cpython-311.pyc
│  │     │  │     ├─ fail_slp_switch.cpython-311.pyc
│  │     │  │     ├─ fail_switch_three_greenlets.cpython-311.pyc
│  │     │  │     ├─ fail_switch_three_greenlets2.cpython-311.pyc
│  │     │  │     ├─ fail_switch_two_greenlets.cpython-311.pyc
│  │     │  │     ├─ leakcheck.cpython-311.pyc
│  │     │  │     ├─ test_contextvars.cpython-311.pyc
│  │     │  │     ├─ test_cpp.cpython-311.pyc
│  │     │  │     ├─ test_extension_interface.cpython-311.pyc
│  │     │  │     ├─ test_gc.cpython-311.pyc
│  │     │  │     ├─ test_generator.cpython-311.pyc
│  │     │  │     ├─ test_generator_nested.cpython-311.pyc
│  │     │  │     ├─ test_greenlet.cpython-311.pyc
│  │     │  │     ├─ test_greenlet_trash.cpython-311.pyc
│  │     │  │     ├─ test_leaks.cpython-311.pyc
│  │     │  │     ├─ test_stack_saved.cpython-311.pyc
│  │     │  │     ├─ test_throw.cpython-311.pyc
│  │     │  │     ├─ test_tracing.cpython-311.pyc
│  │     │  │     ├─ test_version.cpython-311.pyc
│  │     │  │     ├─ test_weakref.cpython-311.pyc
│  │     │  │     └─ __init__.cpython-311.pyc
│  │     │  ├─ TExceptionState.cpp
│  │     │  ├─ TGreenlet.cpp
│  │     │  ├─ TGreenlet.hpp
│  │     │  ├─ TGreenletGlobals.cpp
│  │     │  ├─ TMainGreenlet.cpp
│  │     │  ├─ TPythonState.cpp
│  │     │  ├─ TStackState.cpp
│  │     │  ├─ TThreadState.hpp
│  │     │  ├─ TThreadStateCreator.hpp
│  │     │  ├─ TThreadStateDestroy.cpp
│  │     │  ├─ TUserGreenlet.cpp
│  │     │  ├─ _greenlet.cp311-win_amd64.pyd
│  │     │  ├─ __init__.py
│  │     │  └─ __pycache__
│  │     │     └─ __init__.cpython-311.pyc
│  │     ├─ greenlet-3.2.3.dist-info
│  │     │  ├─ INSTALLER
│  │     │  ├─ licenses
│  │     │  │  ├─ LICENSE
│  │     │  │  └─ LICENSE.PSF
│  │     │  ├─ METADATA
│  │     │  ├─ RECORD
│  │     │  ├─ top_level.txt
│  │     │  └─ WHEEL
│  │     ├─ gunicorn
│  │     │  ├─ app
│  │     │  │  ├─ base.py
│  │     │  │  ├─ pasterapp.py
│  │     │  │  ├─ wsgiapp.py
│  │     │  │  ├─ __init__.py
│  │     │  │  └─ __pycache__
│  │     │  │     ├─ base.cpython-311.pyc
│  │     │  │     ├─ pasterapp.cpython-311.pyc
│  │     │  │     ├─ wsgiapp.cpython-311.pyc
│  │     │  │     └─ __init__.cpython-311.pyc
│  │     │  ├─ arbiter.py
│  │     │  ├─ config.py
│  │     │  ├─ debug.py
│  │     │  ├─ errors.py
│  │     │  ├─ glogging.py
│  │     │  ├─ http
│  │     │  │  ├─ body.py
│  │     │  │  ├─ errors.py
│  │     │  │  ├─ message.py
│  │     │  │  ├─ parser.py
│  │     │  │  ├─ unreader.py
│  │     │  │  ├─ wsgi.py
│  │     │  │  ├─ __init__.py
│  │     │  │  └─ __pycache__
│  │     │  │     ├─ body.cpython-311.pyc
│  │     │  │     ├─ errors.cpython-311.pyc
│  │     │  │     ├─ message.cpython-311.pyc
│  │     │  │     ├─ parser.cpython-311.pyc
│  │     │  │     ├─ unreader.cpython-311.pyc
│  │     │  │     ├─ wsgi.cpython-311.pyc
│  │     │  │     └─ __init__.cpython-311.pyc
│  │     │  ├─ instrument
│  │     │  │  ├─ statsd.py
│  │     │  │  ├─ __init__.py
│  │     │  │  └─ __pycache__
│  │     │  │     ├─ statsd.cpython-311.pyc
│  │     │  │     └─ __init__.cpython-311.pyc
│  │     │  ├─ pidfile.py
│  │     │  ├─ reloader.py
│  │     │  ├─ sock.py
│  │     │  ├─ systemd.py
│  │     │  ├─ util.py
│  │     │  ├─ workers
│  │     │  │  ├─ base.py
│  │     │  │  ├─ base_async.py
│  │     │  │  ├─ geventlet.py
│  │     │  │  ├─ ggevent.py
│  │     │  │  ├─ gthread.py
│  │     │  │  ├─ gtornado.py
│  │     │  │  ├─ sync.py
│  │     │  │  ├─ workertmp.py
│  │     │  │  ├─ __init__.py
│  │     │  │  └─ __pycache__
│  │     │  │     ├─ base.cpython-311.pyc
│  │     │  │     ├─ base_async.cpython-311.pyc
│  │     │  │     ├─ geventlet.cpython-311.pyc
│  │     │  │     ├─ ggevent.cpython-311.pyc
│  │     │  │     ├─ gthread.cpython-311.pyc
│  │     │  │     ├─ gtornado.cpython-311.pyc
│  │     │  │     ├─ sync.cpython-311.pyc
│  │     │  │     ├─ workertmp.cpython-311.pyc
│  │     │  │     └─ __init__.cpython-311.pyc
│  │     │  ├─ __init__.py
│  │     │  ├─ __main__.py
│  │     │  └─ __pycache__
│  │     │     ├─ arbiter.cpython-311.pyc
│  │     │     ├─ config.cpython-311.pyc
│  │     │     ├─ debug.cpython-311.pyc
│  │     │     ├─ errors.cpython-311.pyc
│  │     │     ├─ glogging.cpython-311.pyc
│  │     │     ├─ pidfile.cpython-311.pyc
│  │     │     ├─ reloader.cpython-311.pyc
│  │     │     ├─ sock.cpython-311.pyc
│  │     │     ├─ systemd.cpython-311.pyc
│  │     │     ├─ util.cpython-311.pyc
│  │     │     ├─ __init__.cpython-311.pyc
│  │     │     └─ __main__.cpython-311.pyc
│  │     ├─ gunicorn-23.0.0.dist-info
│  │     │  ├─ entry_points.txt
│  │     │  ├─ INSTALLER
│  │     │  ├─ LICENSE
│  │     │  ├─ METADATA
│  │     │  ├─ RECORD
│  │     │  ├─ REQUESTED
│  │     │  ├─ top_level.txt
│  │     │  └─ WHEEL
│  │     ├─ h11
│  │     │  ├─ py.typed
│  │     │  ├─ _abnf.py
│  │     │  ├─ _connection.py
│  │     │  ├─ _events.py
│  │     │  ├─ _headers.py
│  │     │  ├─ _readers.py
│  │     │  ├─ _receivebuffer.py
│  │     │  ├─ _state.py
│  │     │  ├─ _util.py
│  │     │  ├─ _version.py
│  │     │  ├─ _writers.py
│  │     │  ├─ __init__.py
│  │     │  └─ __pycache__
│  │     │     ├─ _abnf.cpython-311.pyc
│  │     │     ├─ _connection.cpython-311.pyc
│  │     │     ├─ _events.cpython-311.pyc
│  │     │     ├─ _headers.cpython-311.pyc
│  │     │     ├─ _readers.cpython-311.pyc
│  │     │     ├─ _receivebuffer.cpython-311.pyc
│  │     │     ├─ _state.cpython-311.pyc
│  │     │     ├─ _util.cpython-311.pyc
│  │     │     ├─ _version.cpython-311.pyc
│  │     │     ├─ _writers.cpython-311.pyc
│  │     │     └─ __init__.cpython-311.pyc
│  │     ├─ h11-0.16.0.dist-info
│  │     │  ├─ INSTALLER
│  │     │  ├─ licenses
│  │     │  │  └─ LICENSE.txt
│  │     │  ├─ METADATA
│  │     │  ├─ RECORD
│  │     │  ├─ top_level.txt
│  │     │  └─ WHEEL
│  │     ├─ idna
│  │     │  ├─ codec.py
│  │     │  ├─ compat.py
│  │     │  ├─ core.py
│  │     │  ├─ idnadata.py
│  │     │  ├─ intranges.py
│  │     │  ├─ package_data.py
│  │     │  ├─ py.typed
│  │     │  ├─ uts46data.py
│  │     │  ├─ __init__.py
│  │     │  └─ __pycache__
│  │     │     ├─ codec.cpython-311.pyc
│  │     │     ├─ compat.cpython-311.pyc
│  │     │     ├─ core.cpython-311.pyc
│  │     │     ├─ idnadata.cpython-311.pyc
│  │     │     ├─ intranges.cpython-311.pyc
│  │     │     ├─ package_data.cpython-311.pyc
│  │     │     ├─ uts46data.cpython-311.pyc
│  │     │     └─ __init__.cpython-311.pyc
│  │     ├─ idna-3.10.dist-info
│  │     │  ├─ INSTALLER
│  │     │  ├─ LICENSE.md
│  │     │  ├─ METADATA
│  │     │  ├─ RECORD
│  │     │  └─ WHEEL
│  │     ├─ itsdangerous
│  │     │  ├─ encoding.py
│  │     │  ├─ exc.py
│  │     │  ├─ py.typed
│  │     │  ├─ serializer.py
│  │     │  ├─ signer.py
│  │     │  ├─ timed.py
│  │     │  ├─ url_safe.py
│  │     │  ├─ _json.py
│  │     │  ├─ __init__.py
│  │     │  └─ __pycache__
│  │     │     ├─ encoding.cpython-311.pyc
│  │     │     ├─ exc.cpython-311.pyc
│  │     │     ├─ serializer.cpython-311.pyc
│  │     │     ├─ signer.cpython-311.pyc
│  │     │     ├─ timed.cpython-311.pyc
│  │     │     ├─ url_safe.cpython-311.pyc
│  │     │     ├─ _json.cpython-311.pyc
│  │     │     └─ __init__.cpython-311.pyc
│  │     ├─ itsdangerous-2.2.0.dist-info
│  │     │  ├─ INSTALLER
│  │     │  ├─ LICENSE.txt
│  │     │  ├─ METADATA
│  │     │  ├─ RECORD
│  │     │  └─ WHEEL
│  │     ├─ jinja2
│  │     │  ├─ async_utils.py
│  │     │  ├─ bccache.py
│  │     │  ├─ compiler.py
│  │     │  ├─ constants.py
│  │     │  ├─ debug.py
│  │     │  ├─ defaults.py
│  │     │  ├─ environment.py
│  │     │  ├─ exceptions.py
│  │     │  ├─ ext.py
│  │     │  ├─ filters.py
│  │     │  ├─ idtracking.py
│  │     │  ├─ lexer.py
│  │     │  ├─ loaders.py
│  │     │  ├─ meta.py
│  │     │  ├─ nativetypes.py
│  │     │  ├─ nodes.py
│  │     │  ├─ optimizer.py
│  │     │  ├─ parser.py
│  │     │  ├─ py.typed
│  │     │  ├─ runtime.py
│  │     │  ├─ sandbox.py
│  │     │  ├─ tests.py
│  │     │  ├─ utils.py
│  │     │  ├─ visitor.py
│  │     │  ├─ _identifier.py
│  │     │  ├─ __init__.py
│  │     │  └─ __pycache__
│  │     │     ├─ async_utils.cpython-311.pyc
│  │     │     ├─ bccache.cpython-311.pyc
│  │     │     ├─ compiler.cpython-311.pyc
│  │     │     ├─ constants.cpython-311.pyc
│  │     │     ├─ debug.cpython-311.pyc
│  │     │     ├─ defaults.cpython-311.pyc
│  │     │     ├─ environment.cpython-311.pyc
│  │     │     ├─ exceptions.cpython-311.pyc
│  │     │     ├─ ext.cpython-311.pyc
│  │     │     ├─ filters.cpython-311.pyc
│  │     │     ├─ idtracking.cpython-311.pyc
│  │     │     ├─ lexer.cpython-311.pyc
│  │     │     ├─ loaders.cpython-311.pyc
│  │     │     ├─ meta.cpython-311.pyc
│  │     │     ├─ nativetypes.cpython-311.pyc
│  │     │     ├─ nodes.cpython-311.pyc
│  │     │     ├─ optimizer.cpython-311.pyc
│  │     │     ├─ parser.cpython-311.pyc
│  │     │     ├─ runtime.cpython-311.pyc
│  │     │     ├─ sandbox.cpython-311.pyc
│  │     │     ├─ tests.cpython-311.pyc
│  │     │     ├─ utils.cpython-311.pyc
│  │     │     ├─ visitor.cpython-311.pyc
│  │     │     ├─ _identifier.cpython-311.pyc
│  │     │     └─ __init__.cpython-311.pyc
│  │     ├─ jinja2-3.1.6.dist-info
│  │     │  ├─ entry_points.txt
│  │     │  ├─ INSTALLER
│  │     │  ├─ licenses
│  │     │  │  └─ LICENSE.txt
│  │     │  ├─ METADATA
│  │     │  ├─ RECORD
│  │     │  └─ WHEEL
│  │     ├─ markupsafe
│  │     │  ├─ py.typed
│  │     │  ├─ _native.py
│  │     │  ├─ _speedups.c
│  │     │  ├─ _speedups.cp311-win_amd64.pyd
│  │     │  ├─ _speedups.pyi
│  │     │  ├─ __init__.py
│  │     │  └─ __pycache__
│  │     │     ├─ _native.cpython-311.pyc
│  │     │     └─ __init__.cpython-311.pyc
│  │     ├─ MarkupSafe-3.0.2.dist-info
│  │     │  ├─ INSTALLER
│  │     │  ├─ LICENSE.txt
│  │     │  ├─ METADATA
│  │     │  ├─ RECORD
│  │     │  ├─ top_level.txt
│  │     │  └─ WHEEL
│  │     ├─ outcome
│  │     │  ├─ py.typed
│  │     │  ├─ _impl.py
│  │     │  ├─ _util.py
│  │     │  ├─ _version.py
│  │     │  ├─ __init__.py
│  │     │  └─ __pycache__
│  │     │     ├─ _impl.cpython-311.pyc
│  │     │     ├─ _util.cpython-311.pyc
│  │     │     ├─ _version.cpython-311.pyc
│  │     │     └─ __init__.cpython-311.pyc
│  │     ├─ outcome-1.3.0.post0.dist-info
│  │     │  ├─ INSTALLER
│  │     │  ├─ LICENSE
│  │     │  ├─ LICENSE.APACHE2
│  │     │  ├─ LICENSE.MIT
│  │     │  ├─ METADATA
│  │     │  ├─ RECORD
│  │     │  ├─ top_level.txt
│  │     │  └─ WHEEL
│  │     ├─ packaging
│  │     │  ├─ licenses
│  │     │  │  ├─ _spdx.py
│  │     │  │  ├─ __init__.py
│  │     │  │  └─ __pycache__
│  │     │  │     ├─ _spdx.cpython-311.pyc
│  │     │  │     └─ __init__.cpython-311.pyc
│  │     │  ├─ markers.py
│  │     │  ├─ metadata.py
│  │     │  ├─ py.typed
│  │     │  ├─ requirements.py
│  │     │  ├─ specifiers.py
│  │     │  ├─ tags.py
│  │     │  ├─ utils.py
│  │     │  ├─ version.py
│  │     │  ├─ _elffile.py
│  │     │  ├─ _manylinux.py
│  │     │  ├─ _musllinux.py
│  │     │  ├─ _parser.py
│  │     │  ├─ _structures.py
│  │     │  ├─ _tokenizer.py
│  │     │  ├─ __init__.py
│  │     │  └─ __pycache__
│  │     │     ├─ markers.cpython-311.pyc
│  │     │     ├─ metadata.cpython-311.pyc
│  │     │     ├─ requirements.cpython-311.pyc
│  │     │     ├─ specifiers.cpython-311.pyc
│  │     │     ├─ tags.cpython-311.pyc
│  │     │     ├─ utils.cpython-311.pyc
│  │     │     ├─ version.cpython-311.pyc
│  │     │     ├─ _elffile.cpython-311.pyc
│  │     │     ├─ _manylinux.cpython-311.pyc
│  │     │     ├─ _musllinux.cpython-311.pyc
│  │     │     ├─ _parser.cpython-311.pyc
│  │     │     ├─ _structures.cpython-311.pyc
│  │     │     ├─ _tokenizer.cpython-311.pyc
│  │     │     └─ __init__.cpython-311.pyc
│  │     ├─ packaging-25.0.dist-info
│  │     │  ├─ INSTALLER
│  │     │  ├─ licenses
│  │     │  │  ├─ LICENSE
│  │     │  │  ├─ LICENSE.APACHE
│  │     │  │  └─ LICENSE.BSD
│  │     │  ├─ METADATA
│  │     │  ├─ RECORD
│  │     │  └─ WHEEL
│  │     ├─ pip
│  │     │  ├─ py.typed
│  │     │  ├─ _internal
│  │     │  │  ├─ build_env.py
│  │     │  │  ├─ cache.py
│  │     │  │  ├─ cli
│  │     │  │  │  ├─ autocompletion.py
│  │     │  │  │  ├─ base_command.py
│  │     │  │  │  ├─ cmdoptions.py
│  │     │  │  │  ├─ command_context.py
│  │     │  │  │  ├─ main.py
│  │     │  │  │  ├─ main_parser.py
│  │     │  │  │  ├─ parser.py
│  │     │  │  │  ├─ progress_bars.py
│  │     │  │  │  ├─ req_command.py
│  │     │  │  │  ├─ spinners.py
│  │     │  │  │  ├─ status_codes.py
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ autocompletion.cpython-311.pyc
│  │     │  │  │     ├─ base_command.cpython-311.pyc
│  │     │  │  │     ├─ cmdoptions.cpython-311.pyc
│  │     │  │  │     ├─ command_context.cpython-311.pyc
│  │     │  │  │     ├─ main.cpython-311.pyc
│  │     │  │  │     ├─ main_parser.cpython-311.pyc
│  │     │  │  │     ├─ parser.cpython-311.pyc
│  │     │  │  │     ├─ progress_bars.cpython-311.pyc
│  │     │  │  │     ├─ req_command.cpython-311.pyc
│  │     │  │  │     ├─ spinners.cpython-311.pyc
│  │     │  │  │     ├─ status_codes.cpython-311.pyc
│  │     │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  ├─ commands
│  │     │  │  │  ├─ cache.py
│  │     │  │  │  ├─ check.py
│  │     │  │  │  ├─ completion.py
│  │     │  │  │  ├─ configuration.py
│  │     │  │  │  ├─ debug.py
│  │     │  │  │  ├─ download.py
│  │     │  │  │  ├─ freeze.py
│  │     │  │  │  ├─ hash.py
│  │     │  │  │  ├─ help.py
│  │     │  │  │  ├─ index.py
│  │     │  │  │  ├─ inspect.py
│  │     │  │  │  ├─ install.py
│  │     │  │  │  ├─ list.py
│  │     │  │  │  ├─ search.py
│  │     │  │  │  ├─ show.py
│  │     │  │  │  ├─ uninstall.py
│  │     │  │  │  ├─ wheel.py
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ cache.cpython-311.pyc
│  │     │  │  │     ├─ check.cpython-311.pyc
│  │     │  │  │     ├─ completion.cpython-311.pyc
│  │     │  │  │     ├─ configuration.cpython-311.pyc
│  │     │  │  │     ├─ debug.cpython-311.pyc
│  │     │  │  │     ├─ download.cpython-311.pyc
│  │     │  │  │     ├─ freeze.cpython-311.pyc
│  │     │  │  │     ├─ hash.cpython-311.pyc
│  │     │  │  │     ├─ help.cpython-311.pyc
│  │     │  │  │     ├─ index.cpython-311.pyc
│  │     │  │  │     ├─ inspect.cpython-311.pyc
│  │     │  │  │     ├─ install.cpython-311.pyc
│  │     │  │  │     ├─ list.cpython-311.pyc
│  │     │  │  │     ├─ search.cpython-311.pyc
│  │     │  │  │     ├─ show.cpython-311.pyc
│  │     │  │  │     ├─ uninstall.cpython-311.pyc
│  │     │  │  │     ├─ wheel.cpython-311.pyc
│  │     │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  ├─ configuration.py
│  │     │  │  ├─ distributions
│  │     │  │  │  ├─ base.py
│  │     │  │  │  ├─ installed.py
│  │     │  │  │  ├─ sdist.py
│  │     │  │  │  ├─ wheel.py
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ base.cpython-311.pyc
│  │     │  │  │     ├─ installed.cpython-311.pyc
│  │     │  │  │     ├─ sdist.cpython-311.pyc
│  │     │  │  │     ├─ wheel.cpython-311.pyc
│  │     │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  ├─ exceptions.py
│  │     │  │  ├─ index
│  │     │  │  │  ├─ collector.py
│  │     │  │  │  ├─ package_finder.py
│  │     │  │  │  ├─ sources.py
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ collector.cpython-311.pyc
│  │     │  │  │     ├─ package_finder.cpython-311.pyc
│  │     │  │  │     ├─ sources.cpython-311.pyc
│  │     │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  ├─ locations
│  │     │  │  │  ├─ base.py
│  │     │  │  │  ├─ _distutils.py
│  │     │  │  │  ├─ _sysconfig.py
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ base.cpython-311.pyc
│  │     │  │  │     ├─ _distutils.cpython-311.pyc
│  │     │  │  │     ├─ _sysconfig.cpython-311.pyc
│  │     │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  ├─ main.py
│  │     │  │  ├─ metadata
│  │     │  │  │  ├─ base.py
│  │     │  │  │  ├─ importlib
│  │     │  │  │  │  ├─ _compat.py
│  │     │  │  │  │  ├─ _dists.py
│  │     │  │  │  │  ├─ _envs.py
│  │     │  │  │  │  ├─ __init__.py
│  │     │  │  │  │  └─ __pycache__
│  │     │  │  │  │     ├─ _compat.cpython-311.pyc
│  │     │  │  │  │     ├─ _dists.cpython-311.pyc
│  │     │  │  │  │     ├─ _envs.cpython-311.pyc
│  │     │  │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  │  ├─ pkg_resources.py
│  │     │  │  │  ├─ _json.py
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ base.cpython-311.pyc
│  │     │  │  │     ├─ pkg_resources.cpython-311.pyc
│  │     │  │  │     ├─ _json.cpython-311.pyc
│  │     │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  ├─ models
│  │     │  │  │  ├─ candidate.py
│  │     │  │  │  ├─ direct_url.py
│  │     │  │  │  ├─ format_control.py
│  │     │  │  │  ├─ index.py
│  │     │  │  │  ├─ installation_report.py
│  │     │  │  │  ├─ link.py
│  │     │  │  │  ├─ scheme.py
│  │     │  │  │  ├─ search_scope.py
│  │     │  │  │  ├─ selection_prefs.py
│  │     │  │  │  ├─ target_python.py
│  │     │  │  │  ├─ wheel.py
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ candidate.cpython-311.pyc
│  │     │  │  │     ├─ direct_url.cpython-311.pyc
│  │     │  │  │     ├─ format_control.cpython-311.pyc
│  │     │  │  │     ├─ index.cpython-311.pyc
│  │     │  │  │     ├─ installation_report.cpython-311.pyc
│  │     │  │  │     ├─ link.cpython-311.pyc
│  │     │  │  │     ├─ scheme.cpython-311.pyc
│  │     │  │  │     ├─ search_scope.cpython-311.pyc
│  │     │  │  │     ├─ selection_prefs.cpython-311.pyc
│  │     │  │  │     ├─ target_python.cpython-311.pyc
│  │     │  │  │     ├─ wheel.cpython-311.pyc
│  │     │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  ├─ network
│  │     │  │  │  ├─ auth.py
│  │     │  │  │  ├─ cache.py
│  │     │  │  │  ├─ download.py
│  │     │  │  │  ├─ lazy_wheel.py
│  │     │  │  │  ├─ session.py
│  │     │  │  │  ├─ utils.py
│  │     │  │  │  ├─ xmlrpc.py
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ auth.cpython-311.pyc
│  │     │  │  │     ├─ cache.cpython-311.pyc
│  │     │  │  │     ├─ download.cpython-311.pyc
│  │     │  │  │     ├─ lazy_wheel.cpython-311.pyc
│  │     │  │  │     ├─ session.cpython-311.pyc
│  │     │  │  │     ├─ utils.cpython-311.pyc
│  │     │  │  │     ├─ xmlrpc.cpython-311.pyc
│  │     │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  ├─ operations
│  │     │  │  │  ├─ build
│  │     │  │  │  │  ├─ build_tracker.py
│  │     │  │  │  │  ├─ metadata.py
│  │     │  │  │  │  ├─ metadata_editable.py
│  │     │  │  │  │  ├─ metadata_legacy.py
│  │     │  │  │  │  ├─ wheel.py
│  │     │  │  │  │  ├─ wheel_editable.py
│  │     │  │  │  │  ├─ wheel_legacy.py
│  │     │  │  │  │  ├─ __init__.py
│  │     │  │  │  │  └─ __pycache__
│  │     │  │  │  │     ├─ build_tracker.cpython-311.pyc
│  │     │  │  │  │     ├─ metadata.cpython-311.pyc
│  │     │  │  │  │     ├─ metadata_editable.cpython-311.pyc
│  │     │  │  │  │     ├─ metadata_legacy.cpython-311.pyc
│  │     │  │  │  │     ├─ wheel.cpython-311.pyc
│  │     │  │  │  │     ├─ wheel_editable.cpython-311.pyc
│  │     │  │  │  │     ├─ wheel_legacy.cpython-311.pyc
│  │     │  │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  │  ├─ check.py
│  │     │  │  │  ├─ freeze.py
│  │     │  │  │  ├─ install
│  │     │  │  │  │  ├─ editable_legacy.py
│  │     │  │  │  │  ├─ wheel.py
│  │     │  │  │  │  ├─ __init__.py
│  │     │  │  │  │  └─ __pycache__
│  │     │  │  │  │     ├─ editable_legacy.cpython-311.pyc
│  │     │  │  │  │     ├─ wheel.cpython-311.pyc
│  │     │  │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  │  ├─ prepare.py
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ check.cpython-311.pyc
│  │     │  │  │     ├─ freeze.cpython-311.pyc
│  │     │  │  │     ├─ prepare.cpython-311.pyc
│  │     │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  ├─ pyproject.py
│  │     │  │  ├─ req
│  │     │  │  │  ├─ constructors.py
│  │     │  │  │  ├─ req_file.py
│  │     │  │  │  ├─ req_install.py
│  │     │  │  │  ├─ req_set.py
│  │     │  │  │  ├─ req_uninstall.py
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ constructors.cpython-311.pyc
│  │     │  │  │     ├─ req_file.cpython-311.pyc
│  │     │  │  │     ├─ req_install.cpython-311.pyc
│  │     │  │  │     ├─ req_set.cpython-311.pyc
│  │     │  │  │     ├─ req_uninstall.cpython-311.pyc
│  │     │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  ├─ resolution
│  │     │  │  │  ├─ base.py
│  │     │  │  │  ├─ legacy
│  │     │  │  │  │  ├─ resolver.py
│  │     │  │  │  │  ├─ __init__.py
│  │     │  │  │  │  └─ __pycache__
│  │     │  │  │  │     ├─ resolver.cpython-311.pyc
│  │     │  │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  │  ├─ resolvelib
│  │     │  │  │  │  ├─ base.py
│  │     │  │  │  │  ├─ candidates.py
│  │     │  │  │  │  ├─ factory.py
│  │     │  │  │  │  ├─ found_candidates.py
│  │     │  │  │  │  ├─ provider.py
│  │     │  │  │  │  ├─ reporter.py
│  │     │  │  │  │  ├─ requirements.py
│  │     │  │  │  │  ├─ resolver.py
│  │     │  │  │  │  ├─ __init__.py
│  │     │  │  │  │  └─ __pycache__
│  │     │  │  │  │     ├─ base.cpython-311.pyc
│  │     │  │  │  │     ├─ candidates.cpython-311.pyc
│  │     │  │  │  │     ├─ factory.cpython-311.pyc
│  │     │  │  │  │     ├─ found_candidates.cpython-311.pyc
│  │     │  │  │  │     ├─ provider.cpython-311.pyc
│  │     │  │  │  │     ├─ reporter.cpython-311.pyc
│  │     │  │  │  │     ├─ requirements.cpython-311.pyc
│  │     │  │  │  │     ├─ resolver.cpython-311.pyc
│  │     │  │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ base.cpython-311.pyc
│  │     │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  ├─ self_outdated_check.py
│  │     │  │  ├─ utils
│  │     │  │  │  ├─ appdirs.py
│  │     │  │  │  ├─ compat.py
│  │     │  │  │  ├─ compatibility_tags.py
│  │     │  │  │  ├─ datetime.py
│  │     │  │  │  ├─ deprecation.py
│  │     │  │  │  ├─ direct_url_helpers.py
│  │     │  │  │  ├─ egg_link.py
│  │     │  │  │  ├─ encoding.py
│  │     │  │  │  ├─ entrypoints.py
│  │     │  │  │  ├─ filesystem.py
│  │     │  │  │  ├─ filetypes.py
│  │     │  │  │  ├─ glibc.py
│  │     │  │  │  ├─ hashes.py
│  │     │  │  │  ├─ inject_securetransport.py
│  │     │  │  │  ├─ logging.py
│  │     │  │  │  ├─ misc.py
│  │     │  │  │  ├─ models.py
│  │     │  │  │  ├─ packaging.py
│  │     │  │  │  ├─ setuptools_build.py
│  │     │  │  │  ├─ subprocess.py
│  │     │  │  │  ├─ temp_dir.py
│  │     │  │  │  ├─ unpacking.py
│  │     │  │  │  ├─ urls.py
│  │     │  │  │  ├─ virtualenv.py
│  │     │  │  │  ├─ wheel.py
│  │     │  │  │  ├─ _jaraco_text.py
│  │     │  │  │  ├─ _log.py
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ appdirs.cpython-311.pyc
│  │     │  │  │     ├─ compat.cpython-311.pyc
│  │     │  │  │     ├─ compatibility_tags.cpython-311.pyc
│  │     │  │  │     ├─ datetime.cpython-311.pyc
│  │     │  │  │     ├─ deprecation.cpython-311.pyc
│  │     │  │  │     ├─ direct_url_helpers.cpython-311.pyc
│  │     │  │  │     ├─ egg_link.cpython-311.pyc
│  │     │  │  │     ├─ encoding.cpython-311.pyc
│  │     │  │  │     ├─ entrypoints.cpython-311.pyc
│  │     │  │  │     ├─ filesystem.cpython-311.pyc
│  │     │  │  │     ├─ filetypes.cpython-311.pyc
│  │     │  │  │     ├─ glibc.cpython-311.pyc
│  │     │  │  │     ├─ hashes.cpython-311.pyc
│  │     │  │  │     ├─ inject_securetransport.cpython-311.pyc
│  │     │  │  │     ├─ logging.cpython-311.pyc
│  │     │  │  │     ├─ misc.cpython-311.pyc
│  │     │  │  │     ├─ models.cpython-311.pyc
│  │     │  │  │     ├─ packaging.cpython-311.pyc
│  │     │  │  │     ├─ setuptools_build.cpython-311.pyc
│  │     │  │  │     ├─ subprocess.cpython-311.pyc
│  │     │  │  │     ├─ temp_dir.cpython-311.pyc
│  │     │  │  │     ├─ unpacking.cpython-311.pyc
│  │     │  │  │     ├─ urls.cpython-311.pyc
│  │     │  │  │     ├─ virtualenv.cpython-311.pyc
│  │     │  │  │     ├─ wheel.cpython-311.pyc
│  │     │  │  │     ├─ _jaraco_text.cpython-311.pyc
│  │     │  │  │     ├─ _log.cpython-311.pyc
│  │     │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  ├─ vcs
│  │     │  │  │  ├─ bazaar.py
│  │     │  │  │  ├─ git.py
│  │     │  │  │  ├─ mercurial.py
│  │     │  │  │  ├─ subversion.py
│  │     │  │  │  ├─ versioncontrol.py
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ bazaar.cpython-311.pyc
│  │     │  │  │     ├─ git.cpython-311.pyc
│  │     │  │  │     ├─ mercurial.cpython-311.pyc
│  │     │  │  │     ├─ subversion.cpython-311.pyc
│  │     │  │  │     ├─ versioncontrol.cpython-311.pyc
│  │     │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  ├─ wheel_builder.py
│  │     │  │  ├─ __init__.py
│  │     │  │  └─ __pycache__
│  │     │  │     ├─ build_env.cpython-311.pyc
│  │     │  │     ├─ cache.cpython-311.pyc
│  │     │  │     ├─ configuration.cpython-311.pyc
│  │     │  │     ├─ exceptions.cpython-311.pyc
│  │     │  │     ├─ main.cpython-311.pyc
│  │     │  │     ├─ pyproject.cpython-311.pyc
│  │     │  │     ├─ self_outdated_check.cpython-311.pyc
│  │     │  │     ├─ wheel_builder.cpython-311.pyc
│  │     │  │     └─ __init__.cpython-311.pyc
│  │     │  ├─ _vendor
│  │     │  │  ├─ cachecontrol
│  │     │  │  │  ├─ adapter.py
│  │     │  │  │  ├─ cache.py
│  │     │  │  │  ├─ caches
│  │     │  │  │  │  ├─ file_cache.py
│  │     │  │  │  │  ├─ redis_cache.py
│  │     │  │  │  │  ├─ __init__.py
│  │     │  │  │  │  └─ __pycache__
│  │     │  │  │  │     ├─ file_cache.cpython-311.pyc
│  │     │  │  │  │     ├─ redis_cache.cpython-311.pyc
│  │     │  │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  │  ├─ compat.py
│  │     │  │  │  ├─ controller.py
│  │     │  │  │  ├─ filewrapper.py
│  │     │  │  │  ├─ heuristics.py
│  │     │  │  │  ├─ serialize.py
│  │     │  │  │  ├─ wrapper.py
│  │     │  │  │  ├─ _cmd.py
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ adapter.cpython-311.pyc
│  │     │  │  │     ├─ cache.cpython-311.pyc
│  │     │  │  │     ├─ compat.cpython-311.pyc
│  │     │  │  │     ├─ controller.cpython-311.pyc
│  │     │  │  │     ├─ filewrapper.cpython-311.pyc
│  │     │  │  │     ├─ heuristics.cpython-311.pyc
│  │     │  │  │     ├─ serialize.cpython-311.pyc
│  │     │  │  │     ├─ wrapper.cpython-311.pyc
│  │     │  │  │     ├─ _cmd.cpython-311.pyc
│  │     │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  ├─ certifi
│  │     │  │  │  ├─ cacert.pem
│  │     │  │  │  ├─ core.py
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  ├─ __main__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ core.cpython-311.pyc
│  │     │  │  │     ├─ __init__.cpython-311.pyc
│  │     │  │  │     └─ __main__.cpython-311.pyc
│  │     │  │  ├─ chardet
│  │     │  │  │  ├─ big5freq.py
│  │     │  │  │  ├─ big5prober.py
│  │     │  │  │  ├─ chardistribution.py
│  │     │  │  │  ├─ charsetgroupprober.py
│  │     │  │  │  ├─ charsetprober.py
│  │     │  │  │  ├─ cli
│  │     │  │  │  │  ├─ chardetect.py
│  │     │  │  │  │  ├─ __init__.py
│  │     │  │  │  │  └─ __pycache__
│  │     │  │  │  │     ├─ chardetect.cpython-311.pyc
│  │     │  │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  │  ├─ codingstatemachine.py
│  │     │  │  │  ├─ codingstatemachinedict.py
│  │     │  │  │  ├─ cp949prober.py
│  │     │  │  │  ├─ enums.py
│  │     │  │  │  ├─ escprober.py
│  │     │  │  │  ├─ escsm.py
│  │     │  │  │  ├─ eucjpprober.py
│  │     │  │  │  ├─ euckrfreq.py
│  │     │  │  │  ├─ euckrprober.py
│  │     │  │  │  ├─ euctwfreq.py
│  │     │  │  │  ├─ euctwprober.py
│  │     │  │  │  ├─ gb2312freq.py
│  │     │  │  │  ├─ gb2312prober.py
│  │     │  │  │  ├─ hebrewprober.py
│  │     │  │  │  ├─ jisfreq.py
│  │     │  │  │  ├─ johabfreq.py
│  │     │  │  │  ├─ johabprober.py
│  │     │  │  │  ├─ jpcntx.py
│  │     │  │  │  ├─ langbulgarianmodel.py
│  │     │  │  │  ├─ langgreekmodel.py
│  │     │  │  │  ├─ langhebrewmodel.py
│  │     │  │  │  ├─ langhungarianmodel.py
│  │     │  │  │  ├─ langrussianmodel.py
│  │     │  │  │  ├─ langthaimodel.py
│  │     │  │  │  ├─ langturkishmodel.py
│  │     │  │  │  ├─ latin1prober.py
│  │     │  │  │  ├─ macromanprober.py
│  │     │  │  │  ├─ mbcharsetprober.py
│  │     │  │  │  ├─ mbcsgroupprober.py
│  │     │  │  │  ├─ mbcssm.py
│  │     │  │  │  ├─ metadata
│  │     │  │  │  │  ├─ languages.py
│  │     │  │  │  │  ├─ __init__.py
│  │     │  │  │  │  └─ __pycache__
│  │     │  │  │  │     ├─ languages.cpython-311.pyc
│  │     │  │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  │  ├─ resultdict.py
│  │     │  │  │  ├─ sbcharsetprober.py
│  │     │  │  │  ├─ sbcsgroupprober.py
│  │     │  │  │  ├─ sjisprober.py
│  │     │  │  │  ├─ universaldetector.py
│  │     │  │  │  ├─ utf1632prober.py
│  │     │  │  │  ├─ utf8prober.py
│  │     │  │  │  ├─ version.py
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ big5freq.cpython-311.pyc
│  │     │  │  │     ├─ big5prober.cpython-311.pyc
│  │     │  │  │     ├─ chardistribution.cpython-311.pyc
│  │     │  │  │     ├─ charsetgroupprober.cpython-311.pyc
│  │     │  │  │     ├─ charsetprober.cpython-311.pyc
│  │     │  │  │     ├─ codingstatemachine.cpython-311.pyc
│  │     │  │  │     ├─ codingstatemachinedict.cpython-311.pyc
│  │     │  │  │     ├─ cp949prober.cpython-311.pyc
│  │     │  │  │     ├─ enums.cpython-311.pyc
│  │     │  │  │     ├─ escprober.cpython-311.pyc
│  │     │  │  │     ├─ escsm.cpython-311.pyc
│  │     │  │  │     ├─ eucjpprober.cpython-311.pyc
│  │     │  │  │     ├─ euckrfreq.cpython-311.pyc
│  │     │  │  │     ├─ euckrprober.cpython-311.pyc
│  │     │  │  │     ├─ euctwfreq.cpython-311.pyc
│  │     │  │  │     ├─ euctwprober.cpython-311.pyc
│  │     │  │  │     ├─ gb2312freq.cpython-311.pyc
│  │     │  │  │     ├─ gb2312prober.cpython-311.pyc
│  │     │  │  │     ├─ hebrewprober.cpython-311.pyc
│  │     │  │  │     ├─ jisfreq.cpython-311.pyc
│  │     │  │  │     ├─ johabfreq.cpython-311.pyc
│  │     │  │  │     ├─ johabprober.cpython-311.pyc
│  │     │  │  │     ├─ jpcntx.cpython-311.pyc
│  │     │  │  │     ├─ langbulgarianmodel.cpython-311.pyc
│  │     │  │  │     ├─ langgreekmodel.cpython-311.pyc
│  │     │  │  │     ├─ langhebrewmodel.cpython-311.pyc
│  │     │  │  │     ├─ langhungarianmodel.cpython-311.pyc
│  │     │  │  │     ├─ langrussianmodel.cpython-311.pyc
│  │     │  │  │     ├─ langthaimodel.cpython-311.pyc
│  │     │  │  │     ├─ langturkishmodel.cpython-311.pyc
│  │     │  │  │     ├─ latin1prober.cpython-311.pyc
│  │     │  │  │     ├─ macromanprober.cpython-311.pyc
│  │     │  │  │     ├─ mbcharsetprober.cpython-311.pyc
│  │     │  │  │     ├─ mbcsgroupprober.cpython-311.pyc
│  │     │  │  │     ├─ mbcssm.cpython-311.pyc
│  │     │  │  │     ├─ resultdict.cpython-311.pyc
│  │     │  │  │     ├─ sbcharsetprober.cpython-311.pyc
│  │     │  │  │     ├─ sbcsgroupprober.cpython-311.pyc
│  │     │  │  │     ├─ sjisprober.cpython-311.pyc
│  │     │  │  │     ├─ universaldetector.cpython-311.pyc
│  │     │  │  │     ├─ utf1632prober.cpython-311.pyc
│  │     │  │  │     ├─ utf8prober.cpython-311.pyc
│  │     │  │  │     ├─ version.cpython-311.pyc
│  │     │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  ├─ colorama
│  │     │  │  │  ├─ ansi.py
│  │     │  │  │  ├─ ansitowin32.py
│  │     │  │  │  ├─ initialise.py
│  │     │  │  │  ├─ tests
│  │     │  │  │  │  ├─ ansitowin32_test.py
│  │     │  │  │  │  ├─ ansi_test.py
│  │     │  │  │  │  ├─ initialise_test.py
│  │     │  │  │  │  ├─ isatty_test.py
│  │     │  │  │  │  ├─ utils.py
│  │     │  │  │  │  ├─ winterm_test.py
│  │     │  │  │  │  ├─ __init__.py
│  │     │  │  │  │  └─ __pycache__
│  │     │  │  │  │     ├─ ansitowin32_test.cpython-311.pyc
│  │     │  │  │  │     ├─ ansi_test.cpython-311.pyc
│  │     │  │  │  │     ├─ initialise_test.cpython-311.pyc
│  │     │  │  │  │     ├─ isatty_test.cpython-311.pyc
│  │     │  │  │  │     ├─ utils.cpython-311.pyc
│  │     │  │  │  │     ├─ winterm_test.cpython-311.pyc
│  │     │  │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  │  ├─ win32.py
│  │     │  │  │  ├─ winterm.py
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ ansi.cpython-311.pyc
│  │     │  │  │     ├─ ansitowin32.cpython-311.pyc
│  │     │  │  │     ├─ initialise.cpython-311.pyc
│  │     │  │  │     ├─ win32.cpython-311.pyc
│  │     │  │  │     ├─ winterm.cpython-311.pyc
│  │     │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  ├─ distlib
│  │     │  │  │  ├─ compat.py
│  │     │  │  │  ├─ database.py
│  │     │  │  │  ├─ index.py
│  │     │  │  │  ├─ locators.py
│  │     │  │  │  ├─ manifest.py
│  │     │  │  │  ├─ markers.py
│  │     │  │  │  ├─ metadata.py
│  │     │  │  │  ├─ resources.py
│  │     │  │  │  ├─ scripts.py
│  │     │  │  │  ├─ t32.exe
│  │     │  │  │  ├─ t64-arm.exe
│  │     │  │  │  ├─ t64.exe
│  │     │  │  │  ├─ util.py
│  │     │  │  │  ├─ version.py
│  │     │  │  │  ├─ w32.exe
│  │     │  │  │  ├─ w64-arm.exe
│  │     │  │  │  ├─ w64.exe
│  │     │  │  │  ├─ wheel.py
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ compat.cpython-311.pyc
│  │     │  │  │     ├─ database.cpython-311.pyc
│  │     │  │  │     ├─ index.cpython-311.pyc
│  │     │  │  │     ├─ locators.cpython-311.pyc
│  │     │  │  │     ├─ manifest.cpython-311.pyc
│  │     │  │  │     ├─ markers.cpython-311.pyc
│  │     │  │  │     ├─ metadata.cpython-311.pyc
│  │     │  │  │     ├─ resources.cpython-311.pyc
│  │     │  │  │     ├─ scripts.cpython-311.pyc
│  │     │  │  │     ├─ util.cpython-311.pyc
│  │     │  │  │     ├─ version.cpython-311.pyc
│  │     │  │  │     ├─ wheel.cpython-311.pyc
│  │     │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  ├─ distro
│  │     │  │  │  ├─ distro.py
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  ├─ __main__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ distro.cpython-311.pyc
│  │     │  │  │     ├─ __init__.cpython-311.pyc
│  │     │  │  │     └─ __main__.cpython-311.pyc
│  │     │  │  ├─ idna
│  │     │  │  │  ├─ codec.py
│  │     │  │  │  ├─ compat.py
│  │     │  │  │  ├─ core.py
│  │     │  │  │  ├─ idnadata.py
│  │     │  │  │  ├─ intranges.py
│  │     │  │  │  ├─ package_data.py
│  │     │  │  │  ├─ uts46data.py
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ codec.cpython-311.pyc
│  │     │  │  │     ├─ compat.cpython-311.pyc
│  │     │  │  │     ├─ core.cpython-311.pyc
│  │     │  │  │     ├─ idnadata.cpython-311.pyc
│  │     │  │  │     ├─ intranges.cpython-311.pyc
│  │     │  │  │     ├─ package_data.cpython-311.pyc
│  │     │  │  │     ├─ uts46data.cpython-311.pyc
│  │     │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  ├─ msgpack
│  │     │  │  │  ├─ exceptions.py
│  │     │  │  │  ├─ ext.py
│  │     │  │  │  ├─ fallback.py
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ exceptions.cpython-311.pyc
│  │     │  │  │     ├─ ext.cpython-311.pyc
│  │     │  │  │     ├─ fallback.cpython-311.pyc
│  │     │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  ├─ packaging
│  │     │  │  │  ├─ markers.py
│  │     │  │  │  ├─ requirements.py
│  │     │  │  │  ├─ specifiers.py
│  │     │  │  │  ├─ tags.py
│  │     │  │  │  ├─ utils.py
│  │     │  │  │  ├─ version.py
│  │     │  │  │  ├─ _manylinux.py
│  │     │  │  │  ├─ _musllinux.py
│  │     │  │  │  ├─ _structures.py
│  │     │  │  │  ├─ __about__.py
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ markers.cpython-311.pyc
│  │     │  │  │     ├─ requirements.cpython-311.pyc
│  │     │  │  │     ├─ specifiers.cpython-311.pyc
│  │     │  │  │     ├─ tags.cpython-311.pyc
│  │     │  │  │     ├─ utils.cpython-311.pyc
│  │     │  │  │     ├─ version.cpython-311.pyc
│  │     │  │  │     ├─ _manylinux.cpython-311.pyc
│  │     │  │  │     ├─ _musllinux.cpython-311.pyc
│  │     │  │  │     ├─ _structures.cpython-311.pyc
│  │     │  │  │     ├─ __about__.cpython-311.pyc
│  │     │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  ├─ pkg_resources
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  ├─ platformdirs
│  │     │  │  │  ├─ android.py
│  │     │  │  │  ├─ api.py
│  │     │  │  │  ├─ macos.py
│  │     │  │  │  ├─ unix.py
│  │     │  │  │  ├─ version.py
│  │     │  │  │  ├─ windows.py
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  ├─ __main__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ android.cpython-311.pyc
│  │     │  │  │     ├─ api.cpython-311.pyc
│  │     │  │  │     ├─ macos.cpython-311.pyc
│  │     │  │  │     ├─ unix.cpython-311.pyc
│  │     │  │  │     ├─ version.cpython-311.pyc
│  │     │  │  │     ├─ windows.cpython-311.pyc
│  │     │  │  │     ├─ __init__.cpython-311.pyc
│  │     │  │  │     └─ __main__.cpython-311.pyc
│  │     │  │  ├─ pygments
│  │     │  │  │  ├─ cmdline.py
│  │     │  │  │  ├─ console.py
│  │     │  │  │  ├─ filter.py
│  │     │  │  │  ├─ filters
│  │     │  │  │  │  ├─ __init__.py
│  │     │  │  │  │  └─ __pycache__
│  │     │  │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  │  ├─ formatter.py
│  │     │  │  │  ├─ formatters
│  │     │  │  │  │  ├─ bbcode.py
│  │     │  │  │  │  ├─ groff.py
│  │     │  │  │  │  ├─ html.py
│  │     │  │  │  │  ├─ img.py
│  │     │  │  │  │  ├─ irc.py
│  │     │  │  │  │  ├─ latex.py
│  │     │  │  │  │  ├─ other.py
│  │     │  │  │  │  ├─ pangomarkup.py
│  │     │  │  │  │  ├─ rtf.py
│  │     │  │  │  │  ├─ svg.py
│  │     │  │  │  │  ├─ terminal.py
│  │     │  │  │  │  ├─ terminal256.py
│  │     │  │  │  │  ├─ _mapping.py
│  │     │  │  │  │  ├─ __init__.py
│  │     │  │  │  │  └─ __pycache__
│  │     │  │  │  │     ├─ bbcode.cpython-311.pyc
│  │     │  │  │  │     ├─ groff.cpython-311.pyc
│  │     │  │  │  │     ├─ html.cpython-311.pyc
│  │     │  │  │  │     ├─ img.cpython-311.pyc
│  │     │  │  │  │     ├─ irc.cpython-311.pyc
│  │     │  │  │  │     ├─ latex.cpython-311.pyc
│  │     │  │  │  │     ├─ other.cpython-311.pyc
│  │     │  │  │  │     ├─ pangomarkup.cpython-311.pyc
│  │     │  │  │  │     ├─ rtf.cpython-311.pyc
│  │     │  │  │  │     ├─ svg.cpython-311.pyc
│  │     │  │  │  │     ├─ terminal.cpython-311.pyc
│  │     │  │  │  │     ├─ terminal256.cpython-311.pyc
│  │     │  │  │  │     ├─ _mapping.cpython-311.pyc
│  │     │  │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  │  ├─ lexer.py
│  │     │  │  │  ├─ lexers
│  │     │  │  │  │  ├─ python.py
│  │     │  │  │  │  ├─ _mapping.py
│  │     │  │  │  │  ├─ __init__.py
│  │     │  │  │  │  └─ __pycache__
│  │     │  │  │  │     ├─ python.cpython-311.pyc
│  │     │  │  │  │     ├─ _mapping.cpython-311.pyc
│  │     │  │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  │  ├─ modeline.py
│  │     │  │  │  ├─ plugin.py
│  │     │  │  │  ├─ regexopt.py
│  │     │  │  │  ├─ scanner.py
│  │     │  │  │  ├─ sphinxext.py
│  │     │  │  │  ├─ style.py
│  │     │  │  │  ├─ styles
│  │     │  │  │  │  ├─ __init__.py
│  │     │  │  │  │  └─ __pycache__
│  │     │  │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  │  ├─ token.py
│  │     │  │  │  ├─ unistring.py
│  │     │  │  │  ├─ util.py
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  ├─ __main__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ cmdline.cpython-311.pyc
│  │     │  │  │     ├─ console.cpython-311.pyc
│  │     │  │  │     ├─ filter.cpython-311.pyc
│  │     │  │  │     ├─ formatter.cpython-311.pyc
│  │     │  │  │     ├─ lexer.cpython-311.pyc
│  │     │  │  │     ├─ modeline.cpython-311.pyc
│  │     │  │  │     ├─ plugin.cpython-311.pyc
│  │     │  │  │     ├─ regexopt.cpython-311.pyc
│  │     │  │  │     ├─ scanner.cpython-311.pyc
│  │     │  │  │     ├─ sphinxext.cpython-311.pyc
│  │     │  │  │     ├─ style.cpython-311.pyc
│  │     │  │  │     ├─ token.cpython-311.pyc
│  │     │  │  │     ├─ unistring.cpython-311.pyc
│  │     │  │  │     ├─ util.cpython-311.pyc
│  │     │  │  │     ├─ __init__.cpython-311.pyc
│  │     │  │  │     └─ __main__.cpython-311.pyc
│  │     │  │  ├─ pyparsing
│  │     │  │  │  ├─ actions.py
│  │     │  │  │  ├─ common.py
│  │     │  │  │  ├─ core.py
│  │     │  │  │  ├─ diagram
│  │     │  │  │  │  ├─ __init__.py
│  │     │  │  │  │  └─ __pycache__
│  │     │  │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  │  ├─ exceptions.py
│  │     │  │  │  ├─ helpers.py
│  │     │  │  │  ├─ results.py
│  │     │  │  │  ├─ testing.py
│  │     │  │  │  ├─ unicode.py
│  │     │  │  │  ├─ util.py
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ actions.cpython-311.pyc
│  │     │  │  │     ├─ common.cpython-311.pyc
│  │     │  │  │     ├─ core.cpython-311.pyc
│  │     │  │  │     ├─ exceptions.cpython-311.pyc
│  │     │  │  │     ├─ helpers.cpython-311.pyc
│  │     │  │  │     ├─ results.cpython-311.pyc
│  │     │  │  │     ├─ testing.cpython-311.pyc
│  │     │  │  │     ├─ unicode.cpython-311.pyc
│  │     │  │  │     ├─ util.cpython-311.pyc
│  │     │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  ├─ pyproject_hooks
│  │     │  │  │  ├─ _compat.py
│  │     │  │  │  ├─ _impl.py
│  │     │  │  │  ├─ _in_process
│  │     │  │  │  │  ├─ _in_process.py
│  │     │  │  │  │  ├─ __init__.py
│  │     │  │  │  │  └─ __pycache__
│  │     │  │  │  │     ├─ _in_process.cpython-311.pyc
│  │     │  │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ _compat.cpython-311.pyc
│  │     │  │  │     ├─ _impl.cpython-311.pyc
│  │     │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  ├─ requests
│  │     │  │  │  ├─ adapters.py
│  │     │  │  │  ├─ api.py
│  │     │  │  │  ├─ auth.py
│  │     │  │  │  ├─ certs.py
│  │     │  │  │  ├─ compat.py
│  │     │  │  │  ├─ cookies.py
│  │     │  │  │  ├─ exceptions.py
│  │     │  │  │  ├─ help.py
│  │     │  │  │  ├─ hooks.py
│  │     │  │  │  ├─ models.py
│  │     │  │  │  ├─ packages.py
│  │     │  │  │  ├─ sessions.py
│  │     │  │  │  ├─ status_codes.py
│  │     │  │  │  ├─ structures.py
│  │     │  │  │  ├─ utils.py
│  │     │  │  │  ├─ _internal_utils.py
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  ├─ __pycache__
│  │     │  │  │  │  ├─ adapters.cpython-311.pyc
│  │     │  │  │  │  ├─ api.cpython-311.pyc
│  │     │  │  │  │  ├─ auth.cpython-311.pyc
│  │     │  │  │  │  ├─ certs.cpython-311.pyc
│  │     │  │  │  │  ├─ compat.cpython-311.pyc
│  │     │  │  │  │  ├─ cookies.cpython-311.pyc
│  │     │  │  │  │  ├─ exceptions.cpython-311.pyc
│  │     │  │  │  │  ├─ help.cpython-311.pyc
│  │     │  │  │  │  ├─ hooks.cpython-311.pyc
│  │     │  │  │  │  ├─ models.cpython-311.pyc
│  │     │  │  │  │  ├─ packages.cpython-311.pyc
│  │     │  │  │  │  ├─ sessions.cpython-311.pyc
│  │     │  │  │  │  ├─ status_codes.cpython-311.pyc
│  │     │  │  │  │  ├─ structures.cpython-311.pyc
│  │     │  │  │  │  ├─ utils.cpython-311.pyc
│  │     │  │  │  │  ├─ _internal_utils.cpython-311.pyc
│  │     │  │  │  │  ├─ __init__.cpython-311.pyc
│  │     │  │  │  │  └─ __version__.cpython-311.pyc
│  │     │  │  │  └─ __version__.py
│  │     │  │  ├─ resolvelib
│  │     │  │  │  ├─ compat
│  │     │  │  │  │  ├─ collections_abc.py
│  │     │  │  │  │  ├─ __init__.py
│  │     │  │  │  │  └─ __pycache__
│  │     │  │  │  │     ├─ collections_abc.cpython-311.pyc
│  │     │  │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  │  ├─ providers.py
│  │     │  │  │  ├─ reporters.py
│  │     │  │  │  ├─ resolvers.py
│  │     │  │  │  ├─ structs.py
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ providers.cpython-311.pyc
│  │     │  │  │     ├─ reporters.cpython-311.pyc
│  │     │  │  │     ├─ resolvers.cpython-311.pyc
│  │     │  │  │     ├─ structs.cpython-311.pyc
│  │     │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  ├─ rich
│  │     │  │  │  ├─ abc.py
│  │     │  │  │  ├─ align.py
│  │     │  │  │  ├─ ansi.py
│  │     │  │  │  ├─ bar.py
│  │     │  │  │  ├─ box.py
│  │     │  │  │  ├─ cells.py
│  │     │  │  │  ├─ color.py
│  │     │  │  │  ├─ color_triplet.py
│  │     │  │  │  ├─ columns.py
│  │     │  │  │  ├─ console.py
│  │     │  │  │  ├─ constrain.py
│  │     │  │  │  ├─ containers.py
│  │     │  │  │  ├─ control.py
│  │     │  │  │  ├─ default_styles.py
│  │     │  │  │  ├─ diagnose.py
│  │     │  │  │  ├─ emoji.py
│  │     │  │  │  ├─ errors.py
│  │     │  │  │  ├─ filesize.py
│  │     │  │  │  ├─ file_proxy.py
│  │     │  │  │  ├─ highlighter.py
│  │     │  │  │  ├─ json.py
│  │     │  │  │  ├─ jupyter.py
│  │     │  │  │  ├─ layout.py
│  │     │  │  │  ├─ live.py
│  │     │  │  │  ├─ live_render.py
│  │     │  │  │  ├─ logging.py
│  │     │  │  │  ├─ markup.py
│  │     │  │  │  ├─ measure.py
│  │     │  │  │  ├─ padding.py
│  │     │  │  │  ├─ pager.py
│  │     │  │  │  ├─ palette.py
│  │     │  │  │  ├─ panel.py
│  │     │  │  │  ├─ pretty.py
│  │     │  │  │  ├─ progress.py
│  │     │  │  │  ├─ progress_bar.py
│  │     │  │  │  ├─ prompt.py
│  │     │  │  │  ├─ protocol.py
│  │     │  │  │  ├─ region.py
│  │     │  │  │  ├─ repr.py
│  │     │  │  │  ├─ rule.py
│  │     │  │  │  ├─ scope.py
│  │     │  │  │  ├─ screen.py
│  │     │  │  │  ├─ segment.py
│  │     │  │  │  ├─ spinner.py
│  │     │  │  │  ├─ status.py
│  │     │  │  │  ├─ style.py
│  │     │  │  │  ├─ styled.py
│  │     │  │  │  ├─ syntax.py
│  │     │  │  │  ├─ table.py
│  │     │  │  │  ├─ terminal_theme.py
│  │     │  │  │  ├─ text.py
│  │     │  │  │  ├─ theme.py
│  │     │  │  │  ├─ themes.py
│  │     │  │  │  ├─ traceback.py
│  │     │  │  │  ├─ tree.py
│  │     │  │  │  ├─ _cell_widths.py
│  │     │  │  │  ├─ _emoji_codes.py
│  │     │  │  │  ├─ _emoji_replace.py
│  │     │  │  │  ├─ _export_format.py
│  │     │  │  │  ├─ _extension.py
│  │     │  │  │  ├─ _fileno.py
│  │     │  │  │  ├─ _inspect.py
│  │     │  │  │  ├─ _log_render.py
│  │     │  │  │  ├─ _loop.py
│  │     │  │  │  ├─ _null_file.py
│  │     │  │  │  ├─ _palettes.py
│  │     │  │  │  ├─ _pick.py
│  │     │  │  │  ├─ _ratio.py
│  │     │  │  │  ├─ _spinners.py
│  │     │  │  │  ├─ _stack.py
│  │     │  │  │  ├─ _timer.py
│  │     │  │  │  ├─ _win32_console.py
│  │     │  │  │  ├─ _windows.py
│  │     │  │  │  ├─ _windows_renderer.py
│  │     │  │  │  ├─ _wrap.py
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  ├─ __main__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ abc.cpython-311.pyc
│  │     │  │  │     ├─ align.cpython-311.pyc
│  │     │  │  │     ├─ ansi.cpython-311.pyc
│  │     │  │  │     ├─ bar.cpython-311.pyc
│  │     │  │  │     ├─ box.cpython-311.pyc
│  │     │  │  │     ├─ cells.cpython-311.pyc
│  │     │  │  │     ├─ color.cpython-311.pyc
│  │     │  │  │     ├─ color_triplet.cpython-311.pyc
│  │     │  │  │     ├─ columns.cpython-311.pyc
│  │     │  │  │     ├─ console.cpython-311.pyc
│  │     │  │  │     ├─ constrain.cpython-311.pyc
│  │     │  │  │     ├─ containers.cpython-311.pyc
│  │     │  │  │     ├─ control.cpython-311.pyc
│  │     │  │  │     ├─ default_styles.cpython-311.pyc
│  │     │  │  │     ├─ diagnose.cpython-311.pyc
│  │     │  │  │     ├─ emoji.cpython-311.pyc
│  │     │  │  │     ├─ errors.cpython-311.pyc
│  │     │  │  │     ├─ filesize.cpython-311.pyc
│  │     │  │  │     ├─ file_proxy.cpython-311.pyc
│  │     │  │  │     ├─ highlighter.cpython-311.pyc
│  │     │  │  │     ├─ json.cpython-311.pyc
│  │     │  │  │     ├─ jupyter.cpython-311.pyc
│  │     │  │  │     ├─ layout.cpython-311.pyc
│  │     │  │  │     ├─ live.cpython-311.pyc
│  │     │  │  │     ├─ live_render.cpython-311.pyc
│  │     │  │  │     ├─ logging.cpython-311.pyc
│  │     │  │  │     ├─ markup.cpython-311.pyc
│  │     │  │  │     ├─ measure.cpython-311.pyc
│  │     │  │  │     ├─ padding.cpython-311.pyc
│  │     │  │  │     ├─ pager.cpython-311.pyc
│  │     │  │  │     ├─ palette.cpython-311.pyc
│  │     │  │  │     ├─ panel.cpython-311.pyc
│  │     │  │  │     ├─ pretty.cpython-311.pyc
│  │     │  │  │     ├─ progress.cpython-311.pyc
│  │     │  │  │     ├─ progress_bar.cpython-311.pyc
│  │     │  │  │     ├─ prompt.cpython-311.pyc
│  │     │  │  │     ├─ protocol.cpython-311.pyc
│  │     │  │  │     ├─ region.cpython-311.pyc
│  │     │  │  │     ├─ repr.cpython-311.pyc
│  │     │  │  │     ├─ rule.cpython-311.pyc
│  │     │  │  │     ├─ scope.cpython-311.pyc
│  │     │  │  │     ├─ screen.cpython-311.pyc
│  │     │  │  │     ├─ segment.cpython-311.pyc
│  │     │  │  │     ├─ spinner.cpython-311.pyc
│  │     │  │  │     ├─ status.cpython-311.pyc
│  │     │  │  │     ├─ style.cpython-311.pyc
│  │     │  │  │     ├─ styled.cpython-311.pyc
│  │     │  │  │     ├─ syntax.cpython-311.pyc
│  │     │  │  │     ├─ table.cpython-311.pyc
│  │     │  │  │     ├─ terminal_theme.cpython-311.pyc
│  │     │  │  │     ├─ text.cpython-311.pyc
│  │     │  │  │     ├─ theme.cpython-311.pyc
│  │     │  │  │     ├─ themes.cpython-311.pyc
│  │     │  │  │     ├─ traceback.cpython-311.pyc
│  │     │  │  │     ├─ tree.cpython-311.pyc
│  │     │  │  │     ├─ _cell_widths.cpython-311.pyc
│  │     │  │  │     ├─ _emoji_codes.cpython-311.pyc
│  │     │  │  │     ├─ _emoji_replace.cpython-311.pyc
│  │     │  │  │     ├─ _export_format.cpython-311.pyc
│  │     │  │  │     ├─ _extension.cpython-311.pyc
│  │     │  │  │     ├─ _fileno.cpython-311.pyc
│  │     │  │  │     ├─ _inspect.cpython-311.pyc
│  │     │  │  │     ├─ _log_render.cpython-311.pyc
│  │     │  │  │     ├─ _loop.cpython-311.pyc
│  │     │  │  │     ├─ _null_file.cpython-311.pyc
│  │     │  │  │     ├─ _palettes.cpython-311.pyc
│  │     │  │  │     ├─ _pick.cpython-311.pyc
│  │     │  │  │     ├─ _ratio.cpython-311.pyc
│  │     │  │  │     ├─ _spinners.cpython-311.pyc
│  │     │  │  │     ├─ _stack.cpython-311.pyc
│  │     │  │  │     ├─ _timer.cpython-311.pyc
│  │     │  │  │     ├─ _win32_console.cpython-311.pyc
│  │     │  │  │     ├─ _windows.cpython-311.pyc
│  │     │  │  │     ├─ _windows_renderer.cpython-311.pyc
│  │     │  │  │     ├─ _wrap.cpython-311.pyc
│  │     │  │  │     ├─ __init__.cpython-311.pyc
│  │     │  │  │     └─ __main__.cpython-311.pyc
│  │     │  │  ├─ six.py
│  │     │  │  ├─ tenacity
│  │     │  │  │  ├─ after.py
│  │     │  │  │  ├─ before.py
│  │     │  │  │  ├─ before_sleep.py
│  │     │  │  │  ├─ nap.py
│  │     │  │  │  ├─ retry.py
│  │     │  │  │  ├─ stop.py
│  │     │  │  │  ├─ tornadoweb.py
│  │     │  │  │  ├─ wait.py
│  │     │  │  │  ├─ _asyncio.py
│  │     │  │  │  ├─ _utils.py
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ after.cpython-311.pyc
│  │     │  │  │     ├─ before.cpython-311.pyc
│  │     │  │  │     ├─ before_sleep.cpython-311.pyc
│  │     │  │  │     ├─ nap.cpython-311.pyc
│  │     │  │  │     ├─ retry.cpython-311.pyc
│  │     │  │  │     ├─ stop.cpython-311.pyc
│  │     │  │  │     ├─ tornadoweb.cpython-311.pyc
│  │     │  │  │     ├─ wait.cpython-311.pyc
│  │     │  │  │     ├─ _asyncio.cpython-311.pyc
│  │     │  │  │     ├─ _utils.cpython-311.pyc
│  │     │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  ├─ tomli
│  │     │  │  │  ├─ _parser.py
│  │     │  │  │  ├─ _re.py
│  │     │  │  │  ├─ _types.py
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ _parser.cpython-311.pyc
│  │     │  │  │     ├─ _re.cpython-311.pyc
│  │     │  │  │     ├─ _types.cpython-311.pyc
│  │     │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  ├─ typing_extensions.py
│  │     │  │  ├─ urllib3
│  │     │  │  │  ├─ connection.py
│  │     │  │  │  ├─ connectionpool.py
│  │     │  │  │  ├─ contrib
│  │     │  │  │  │  ├─ appengine.py
│  │     │  │  │  │  ├─ ntlmpool.py
│  │     │  │  │  │  ├─ pyopenssl.py
│  │     │  │  │  │  ├─ securetransport.py
│  │     │  │  │  │  ├─ socks.py
│  │     │  │  │  │  ├─ _appengine_environ.py
│  │     │  │  │  │  ├─ _securetransport
│  │     │  │  │  │  │  ├─ bindings.py
│  │     │  │  │  │  │  ├─ low_level.py
│  │     │  │  │  │  │  ├─ __init__.py
│  │     │  │  │  │  │  └─ __pycache__
│  │     │  │  │  │  │     ├─ bindings.cpython-311.pyc
│  │     │  │  │  │  │     ├─ low_level.cpython-311.pyc
│  │     │  │  │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  │  │  ├─ __init__.py
│  │     │  │  │  │  └─ __pycache__
│  │     │  │  │  │     ├─ appengine.cpython-311.pyc
│  │     │  │  │  │     ├─ ntlmpool.cpython-311.pyc
│  │     │  │  │  │     ├─ pyopenssl.cpython-311.pyc
│  │     │  │  │  │     ├─ securetransport.cpython-311.pyc
│  │     │  │  │  │     ├─ socks.cpython-311.pyc
│  │     │  │  │  │     ├─ _appengine_environ.cpython-311.pyc
│  │     │  │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  │  ├─ exceptions.py
│  │     │  │  │  ├─ fields.py
│  │     │  │  │  ├─ filepost.py
│  │     │  │  │  ├─ packages
│  │     │  │  │  │  ├─ backports
│  │     │  │  │  │  │  ├─ makefile.py
│  │     │  │  │  │  │  ├─ weakref_finalize.py
│  │     │  │  │  │  │  ├─ __init__.py
│  │     │  │  │  │  │  └─ __pycache__
│  │     │  │  │  │  │     ├─ makefile.cpython-311.pyc
│  │     │  │  │  │  │     ├─ weakref_finalize.cpython-311.pyc
│  │     │  │  │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  │  │  ├─ six.py
│  │     │  │  │  │  ├─ __init__.py
│  │     │  │  │  │  └─ __pycache__
│  │     │  │  │  │     ├─ six.cpython-311.pyc
│  │     │  │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  │  ├─ poolmanager.py
│  │     │  │  │  ├─ request.py
│  │     │  │  │  ├─ response.py
│  │     │  │  │  ├─ util
│  │     │  │  │  │  ├─ connection.py
│  │     │  │  │  │  ├─ proxy.py
│  │     │  │  │  │  ├─ queue.py
│  │     │  │  │  │  ├─ request.py
│  │     │  │  │  │  ├─ response.py
│  │     │  │  │  │  ├─ retry.py
│  │     │  │  │  │  ├─ ssltransport.py
│  │     │  │  │  │  ├─ ssl_.py
│  │     │  │  │  │  ├─ ssl_match_hostname.py
│  │     │  │  │  │  ├─ timeout.py
│  │     │  │  │  │  ├─ url.py
│  │     │  │  │  │  ├─ wait.py
│  │     │  │  │  │  ├─ __init__.py
│  │     │  │  │  │  └─ __pycache__
│  │     │  │  │  │     ├─ connection.cpython-311.pyc
│  │     │  │  │  │     ├─ proxy.cpython-311.pyc
│  │     │  │  │  │     ├─ queue.cpython-311.pyc
│  │     │  │  │  │     ├─ request.cpython-311.pyc
│  │     │  │  │  │     ├─ response.cpython-311.pyc
│  │     │  │  │  │     ├─ retry.cpython-311.pyc
│  │     │  │  │  │     ├─ ssltransport.cpython-311.pyc
│  │     │  │  │  │     ├─ ssl_.cpython-311.pyc
│  │     │  │  │  │     ├─ ssl_match_hostname.cpython-311.pyc
│  │     │  │  │  │     ├─ timeout.cpython-311.pyc
│  │     │  │  │  │     ├─ url.cpython-311.pyc
│  │     │  │  │  │     ├─ wait.cpython-311.pyc
│  │     │  │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  │  ├─ _collections.py
│  │     │  │  │  ├─ _version.py
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ connection.cpython-311.pyc
│  │     │  │  │     ├─ connectionpool.cpython-311.pyc
│  │     │  │  │     ├─ exceptions.cpython-311.pyc
│  │     │  │  │     ├─ fields.cpython-311.pyc
│  │     │  │  │     ├─ filepost.cpython-311.pyc
│  │     │  │  │     ├─ poolmanager.cpython-311.pyc
│  │     │  │  │     ├─ request.cpython-311.pyc
│  │     │  │  │     ├─ response.cpython-311.pyc
│  │     │  │  │     ├─ _collections.cpython-311.pyc
│  │     │  │  │     ├─ _version.cpython-311.pyc
│  │     │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  ├─ vendor.txt
│  │     │  │  ├─ webencodings
│  │     │  │  │  ├─ labels.py
│  │     │  │  │  ├─ mklabels.py
│  │     │  │  │  ├─ tests.py
│  │     │  │  │  ├─ x_user_defined.py
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ labels.cpython-311.pyc
│  │     │  │  │     ├─ mklabels.cpython-311.pyc
│  │     │  │  │     ├─ tests.cpython-311.pyc
│  │     │  │  │     ├─ x_user_defined.cpython-311.pyc
│  │     │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  ├─ __init__.py
│  │     │  │  └─ __pycache__
│  │     │  │     ├─ six.cpython-311.pyc
│  │     │  │     ├─ typing_extensions.cpython-311.pyc
│  │     │  │     └─ __init__.cpython-311.pyc
│  │     │  ├─ __init__.py
│  │     │  ├─ __main__.py
│  │     │  ├─ __pip-runner__.py
│  │     │  └─ __pycache__
│  │     │     ├─ __init__.cpython-311.pyc
│  │     │     ├─ __main__.cpython-311.pyc
│  │     │     └─ __pip-runner__.cpython-311.pyc
│  │     ├─ pip-23.2.1.dist-info
│  │     │  ├─ AUTHORS.txt
│  │     │  ├─ entry_points.txt
│  │     │  ├─ INSTALLER
│  │     │  ├─ LICENSE.txt
│  │     │  ├─ METADATA
│  │     │  ├─ RECORD
│  │     │  ├─ REQUESTED
│  │     │  ├─ top_level.txt
│  │     │  └─ WHEEL
│  │     ├─ pkg_resources
│  │     │  ├─ extern
│  │     │  │  ├─ __init__.py
│  │     │  │  └─ __pycache__
│  │     │  │     └─ __init__.cpython-311.pyc
│  │     │  ├─ _vendor
│  │     │  │  ├─ appdirs.py
│  │     │  │  ├─ importlib_resources
│  │     │  │  │  ├─ abc.py
│  │     │  │  │  ├─ readers.py
│  │     │  │  │  ├─ simple.py
│  │     │  │  │  ├─ _adapters.py
│  │     │  │  │  ├─ _common.py
│  │     │  │  │  ├─ _compat.py
│  │     │  │  │  ├─ _itertools.py
│  │     │  │  │  ├─ _legacy.py
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ abc.cpython-311.pyc
│  │     │  │  │     ├─ readers.cpython-311.pyc
│  │     │  │  │     ├─ simple.cpython-311.pyc
│  │     │  │  │     ├─ _adapters.cpython-311.pyc
│  │     │  │  │     ├─ _common.cpython-311.pyc
│  │     │  │  │     ├─ _compat.cpython-311.pyc
│  │     │  │  │     ├─ _itertools.cpython-311.pyc
│  │     │  │  │     ├─ _legacy.cpython-311.pyc
│  │     │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  ├─ jaraco
│  │     │  │  │  ├─ context.py
│  │     │  │  │  ├─ functools.py
│  │     │  │  │  ├─ text
│  │     │  │  │  │  ├─ __init__.py
│  │     │  │  │  │  └─ __pycache__
│  │     │  │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ context.cpython-311.pyc
│  │     │  │  │     ├─ functools.cpython-311.pyc
│  │     │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  ├─ more_itertools
│  │     │  │  │  ├─ more.py
│  │     │  │  │  ├─ recipes.py
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ more.cpython-311.pyc
│  │     │  │  │     ├─ recipes.cpython-311.pyc
│  │     │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  ├─ packaging
│  │     │  │  │  ├─ markers.py
│  │     │  │  │  ├─ requirements.py
│  │     │  │  │  ├─ specifiers.py
│  │     │  │  │  ├─ tags.py
│  │     │  │  │  ├─ utils.py
│  │     │  │  │  ├─ version.py
│  │     │  │  │  ├─ _manylinux.py
│  │     │  │  │  ├─ _musllinux.py
│  │     │  │  │  ├─ _structures.py
│  │     │  │  │  ├─ __about__.py
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ markers.cpython-311.pyc
│  │     │  │  │     ├─ requirements.cpython-311.pyc
│  │     │  │  │     ├─ specifiers.cpython-311.pyc
│  │     │  │  │     ├─ tags.cpython-311.pyc
│  │     │  │  │     ├─ utils.cpython-311.pyc
│  │     │  │  │     ├─ version.cpython-311.pyc
│  │     │  │  │     ├─ _manylinux.cpython-311.pyc
│  │     │  │  │     ├─ _musllinux.cpython-311.pyc
│  │     │  │  │     ├─ _structures.cpython-311.pyc
│  │     │  │  │     ├─ __about__.cpython-311.pyc
│  │     │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  ├─ pyparsing
│  │     │  │  │  ├─ actions.py
│  │     │  │  │  ├─ common.py
│  │     │  │  │  ├─ core.py
│  │     │  │  │  ├─ diagram
│  │     │  │  │  │  ├─ __init__.py
│  │     │  │  │  │  └─ __pycache__
│  │     │  │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  │  ├─ exceptions.py
│  │     │  │  │  ├─ helpers.py
│  │     │  │  │  ├─ results.py
│  │     │  │  │  ├─ testing.py
│  │     │  │  │  ├─ unicode.py
│  │     │  │  │  ├─ util.py
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ actions.cpython-311.pyc
│  │     │  │  │     ├─ common.cpython-311.pyc
│  │     │  │  │     ├─ core.cpython-311.pyc
│  │     │  │  │     ├─ exceptions.cpython-311.pyc
│  │     │  │  │     ├─ helpers.cpython-311.pyc
│  │     │  │  │     ├─ results.cpython-311.pyc
│  │     │  │  │     ├─ testing.cpython-311.pyc
│  │     │  │  │     ├─ unicode.cpython-311.pyc
│  │     │  │  │     ├─ util.cpython-311.pyc
│  │     │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  ├─ zipp.py
│  │     │  │  ├─ __init__.py
│  │     │  │  └─ __pycache__
│  │     │  │     ├─ appdirs.cpython-311.pyc
│  │     │  │     ├─ zipp.cpython-311.pyc
│  │     │  │     └─ __init__.cpython-311.pyc
│  │     │  ├─ __init__.py
│  │     │  └─ __pycache__
│  │     │     └─ __init__.cpython-311.pyc
│  │     ├─ psycopg2
│  │     │  ├─ errorcodes.py
│  │     │  ├─ errors.py
│  │     │  ├─ extensions.py
│  │     │  ├─ extras.py
│  │     │  ├─ pool.py
│  │     │  ├─ sql.py
│  │     │  ├─ tz.py
│  │     │  ├─ _ipaddress.py
│  │     │  ├─ _json.py
│  │     │  ├─ _psycopg.cp311-win_amd64.pyd
│  │     │  ├─ _range.py
│  │     │  ├─ __init__.py
│  │     │  └─ __pycache__
│  │     │     ├─ errorcodes.cpython-311.pyc
│  │     │     ├─ errors.cpython-311.pyc
│  │     │     ├─ extensions.cpython-311.pyc
│  │     │     ├─ extras.cpython-311.pyc
│  │     │     ├─ pool.cpython-311.pyc
│  │     │     ├─ sql.cpython-311.pyc
│  │     │     ├─ tz.cpython-311.pyc
│  │     │     ├─ _ipaddress.cpython-311.pyc
│  │     │     ├─ _json.cpython-311.pyc
│  │     │     ├─ _range.cpython-311.pyc
│  │     │     └─ __init__.cpython-311.pyc
│  │     ├─ psycopg2_binary-2.9.10.dist-info
│  │     │  ├─ INSTALLER
│  │     │  ├─ LICENSE
│  │     │  ├─ METADATA
│  │     │  ├─ RECORD
│  │     │  ├─ REQUESTED
│  │     │  ├─ top_level.txt
│  │     │  └─ WHEEL
│  │     ├─ pycparser
│  │     │  ├─ ast_transforms.py
│  │     │  ├─ c_ast.py
│  │     │  ├─ c_generator.py
│  │     │  ├─ c_lexer.py
│  │     │  ├─ c_parser.py
│  │     │  ├─ lextab.py
│  │     │  ├─ ply
│  │     │  │  ├─ cpp.py
│  │     │  │  ├─ ctokens.py
│  │     │  │  ├─ lex.py
│  │     │  │  ├─ yacc.py
│  │     │  │  ├─ ygen.py
│  │     │  │  ├─ __init__.py
│  │     │  │  └─ __pycache__
│  │     │  │     ├─ cpp.cpython-311.pyc
│  │     │  │     ├─ ctokens.cpython-311.pyc
│  │     │  │     ├─ lex.cpython-311.pyc
│  │     │  │     ├─ yacc.cpython-311.pyc
│  │     │  │     ├─ ygen.cpython-311.pyc
│  │     │  │     └─ __init__.cpython-311.pyc
│  │     │  ├─ plyparser.py
│  │     │  ├─ yacctab.py
│  │     │  ├─ _ast_gen.py
│  │     │  ├─ _build_tables.py
│  │     │  ├─ _c_ast.cfg
│  │     │  ├─ __init__.py
│  │     │  └─ __pycache__
│  │     │     ├─ ast_transforms.cpython-311.pyc
│  │     │     ├─ c_ast.cpython-311.pyc
│  │     │     ├─ c_generator.cpython-311.pyc
│  │     │     ├─ c_lexer.cpython-311.pyc
│  │     │     ├─ c_parser.cpython-311.pyc
│  │     │     ├─ lextab.cpython-311.pyc
│  │     │     ├─ plyparser.cpython-311.pyc
│  │     │     ├─ yacctab.cpython-311.pyc
│  │     │     ├─ _ast_gen.cpython-311.pyc
│  │     │     ├─ _build_tables.cpython-311.pyc
│  │     │     └─ __init__.cpython-311.pyc
│  │     ├─ pycparser-2.22.dist-info
│  │     │  ├─ INSTALLER
│  │     │  ├─ LICENSE
│  │     │  ├─ METADATA
│  │     │  ├─ RECORD
│  │     │  ├─ top_level.txt
│  │     │  └─ WHEEL
│  │     ├─ PySocks-1.7.1.dist-info
│  │     │  ├─ INSTALLER
│  │     │  ├─ LICENSE
│  │     │  ├─ METADATA
│  │     │  ├─ RECORD
│  │     │  ├─ top_level.txt
│  │     │  └─ WHEEL
│  │     ├─ python_dotenv-1.1.1.dist-info
│  │     │  ├─ entry_points.txt
│  │     │  ├─ INSTALLER
│  │     │  ├─ licenses
│  │     │  │  └─ LICENSE
│  │     │  ├─ METADATA
│  │     │  ├─ RECORD
│  │     │  ├─ REQUESTED
│  │     │  ├─ top_level.txt
│  │     │  └─ WHEEL
│  │     ├─ requests
│  │     │  ├─ adapters.py
│  │     │  ├─ api.py
│  │     │  ├─ auth.py
│  │     │  ├─ certs.py
│  │     │  ├─ compat.py
│  │     │  ├─ cookies.py
│  │     │  ├─ exceptions.py
│  │     │  ├─ help.py
│  │     │  ├─ hooks.py
│  │     │  ├─ models.py
│  │     │  ├─ packages.py
│  │     │  ├─ sessions.py
│  │     │  ├─ status_codes.py
│  │     │  ├─ structures.py
│  │     │  ├─ utils.py
│  │     │  ├─ _internal_utils.py
│  │     │  ├─ __init__.py
│  │     │  ├─ __pycache__
│  │     │  │  ├─ adapters.cpython-311.pyc
│  │     │  │  ├─ api.cpython-311.pyc
│  │     │  │  ├─ auth.cpython-311.pyc
│  │     │  │  ├─ certs.cpython-311.pyc
│  │     │  │  ├─ compat.cpython-311.pyc
│  │     │  │  ├─ cookies.cpython-311.pyc
│  │     │  │  ├─ exceptions.cpython-311.pyc
│  │     │  │  ├─ help.cpython-311.pyc
│  │     │  │  ├─ hooks.cpython-311.pyc
│  │     │  │  ├─ models.cpython-311.pyc
│  │     │  │  ├─ packages.cpython-311.pyc
│  │     │  │  ├─ sessions.cpython-311.pyc
│  │     │  │  ├─ status_codes.cpython-311.pyc
│  │     │  │  ├─ structures.cpython-311.pyc
│  │     │  │  ├─ utils.cpython-311.pyc
│  │     │  │  ├─ _internal_utils.cpython-311.pyc
│  │     │  │  ├─ __init__.cpython-311.pyc
│  │     │  │  └─ __version__.cpython-311.pyc
│  │     │  └─ __version__.py
│  │     ├─ requests-2.32.4.dist-info
│  │     │  ├─ INSTALLER
│  │     │  ├─ licenses
│  │     │  │  └─ LICENSE
│  │     │  ├─ METADATA
│  │     │  ├─ RECORD
│  │     │  ├─ top_level.txt
│  │     │  └─ WHEEL
│  │     ├─ selenium
│  │     │  ├─ common
│  │     │  │  ├─ exceptions.py
│  │     │  │  ├─ __init__.py
│  │     │  │  └─ __pycache__
│  │     │  │     ├─ exceptions.cpython-311.pyc
│  │     │  │     └─ __init__.cpython-311.pyc
│  │     │  ├─ py.typed
│  │     │  ├─ types.py
│  │     │  ├─ webdriver
│  │     │  │  ├─ chrome
│  │     │  │  │  ├─ options.py
│  │     │  │  │  ├─ remote_connection.py
│  │     │  │  │  ├─ service.py
│  │     │  │  │  ├─ webdriver.py
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ options.cpython-311.pyc
│  │     │  │  │     ├─ remote_connection.cpython-311.pyc
│  │     │  │  │     ├─ service.cpython-311.pyc
│  │     │  │  │     ├─ webdriver.cpython-311.pyc
│  │     │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  ├─ chromium
│  │     │  │  │  ├─ options.py
│  │     │  │  │  ├─ remote_connection.py
│  │     │  │  │  ├─ service.py
│  │     │  │  │  ├─ webdriver.py
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ options.cpython-311.pyc
│  │     │  │  │     ├─ remote_connection.cpython-311.pyc
│  │     │  │  │     ├─ service.cpython-311.pyc
│  │     │  │  │     ├─ webdriver.cpython-311.pyc
│  │     │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  ├─ common
│  │     │  │  │  ├─ actions
│  │     │  │  │  │  ├─ action_builder.py
│  │     │  │  │  │  ├─ input_device.py
│  │     │  │  │  │  ├─ interaction.py
│  │     │  │  │  │  ├─ key_actions.py
│  │     │  │  │  │  ├─ key_input.py
│  │     │  │  │  │  ├─ mouse_button.py
│  │     │  │  │  │  ├─ pointer_actions.py
│  │     │  │  │  │  ├─ pointer_input.py
│  │     │  │  │  │  ├─ wheel_actions.py
│  │     │  │  │  │  ├─ wheel_input.py
│  │     │  │  │  │  ├─ __init__.py
│  │     │  │  │  │  └─ __pycache__
│  │     │  │  │  │     ├─ action_builder.cpython-311.pyc
│  │     │  │  │  │     ├─ input_device.cpython-311.pyc
│  │     │  │  │  │     ├─ interaction.cpython-311.pyc
│  │     │  │  │  │     ├─ key_actions.cpython-311.pyc
│  │     │  │  │  │     ├─ key_input.cpython-311.pyc
│  │     │  │  │  │     ├─ mouse_button.cpython-311.pyc
│  │     │  │  │  │     ├─ pointer_actions.cpython-311.pyc
│  │     │  │  │  │     ├─ pointer_input.cpython-311.pyc
│  │     │  │  │  │     ├─ wheel_actions.cpython-311.pyc
│  │     │  │  │  │     ├─ wheel_input.cpython-311.pyc
│  │     │  │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  │  ├─ action_chains.py
│  │     │  │  │  ├─ alert.py
│  │     │  │  │  ├─ bidi
│  │     │  │  │  │  ├─ browser.py
│  │     │  │  │  │  ├─ browsing_context.py
│  │     │  │  │  │  ├─ cdp.py
│  │     │  │  │  │  ├─ common.py
│  │     │  │  │  │  ├─ console.py
│  │     │  │  │  │  ├─ log.py
│  │     │  │  │  │  ├─ network.py
│  │     │  │  │  │  ├─ permissions.py
│  │     │  │  │  │  ├─ script.py
│  │     │  │  │  │  ├─ session.py
│  │     │  │  │  │  ├─ storage.py
│  │     │  │  │  │  ├─ webextension.py
│  │     │  │  │  │  ├─ __init__.py
│  │     │  │  │  │  └─ __pycache__
│  │     │  │  │  │     ├─ browser.cpython-311.pyc
│  │     │  │  │  │     ├─ browsing_context.cpython-311.pyc
│  │     │  │  │  │     ├─ cdp.cpython-311.pyc
│  │     │  │  │  │     ├─ common.cpython-311.pyc
│  │     │  │  │  │     ├─ console.cpython-311.pyc
│  │     │  │  │  │     ├─ log.cpython-311.pyc
│  │     │  │  │  │     ├─ network.cpython-311.pyc
│  │     │  │  │  │     ├─ permissions.cpython-311.pyc
│  │     │  │  │  │     ├─ script.cpython-311.pyc
│  │     │  │  │  │     ├─ session.cpython-311.pyc
│  │     │  │  │  │     ├─ storage.cpython-311.pyc
│  │     │  │  │  │     ├─ webextension.cpython-311.pyc
│  │     │  │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  │  ├─ by.py
│  │     │  │  │  ├─ desired_capabilities.py
│  │     │  │  │  ├─ devtools
│  │     │  │  │  │  ├─ v136
│  │     │  │  │  │  │  ├─ accessibility.py
│  │     │  │  │  │  │  ├─ animation.py
│  │     │  │  │  │  │  ├─ audits.py
│  │     │  │  │  │  │  ├─ autofill.py
│  │     │  │  │  │  │  ├─ background_service.py
│  │     │  │  │  │  │  ├─ bluetooth_emulation.py
│  │     │  │  │  │  │  ├─ browser.py
│  │     │  │  │  │  │  ├─ cache_storage.py
│  │     │  │  │  │  │  ├─ cast.py
│  │     │  │  │  │  │  ├─ console.py
│  │     │  │  │  │  │  ├─ css.py
│  │     │  │  │  │  │  ├─ debugger.py
│  │     │  │  │  │  │  ├─ device_access.py
│  │     │  │  │  │  │  ├─ device_orientation.py
│  │     │  │  │  │  │  ├─ dom.py
│  │     │  │  │  │  │  ├─ dom_debugger.py
│  │     │  │  │  │  │  ├─ dom_snapshot.py
│  │     │  │  │  │  │  ├─ dom_storage.py
│  │     │  │  │  │  │  ├─ emulation.py
│  │     │  │  │  │  │  ├─ event_breakpoints.py
│  │     │  │  │  │  │  ├─ extensions.py
│  │     │  │  │  │  │  ├─ fed_cm.py
│  │     │  │  │  │  │  ├─ fetch.py
│  │     │  │  │  │  │  ├─ file_system.py
│  │     │  │  │  │  │  ├─ headless_experimental.py
│  │     │  │  │  │  │  ├─ heap_profiler.py
│  │     │  │  │  │  │  ├─ indexed_db.py
│  │     │  │  │  │  │  ├─ input_.py
│  │     │  │  │  │  │  ├─ inspector.py
│  │     │  │  │  │  │  ├─ io.py
│  │     │  │  │  │  │  ├─ layer_tree.py
│  │     │  │  │  │  │  ├─ log.py
│  │     │  │  │  │  │  ├─ media.py
│  │     │  │  │  │  │  ├─ memory.py
│  │     │  │  │  │  │  ├─ network.py
│  │     │  │  │  │  │  ├─ overlay.py
│  │     │  │  │  │  │  ├─ page.py
│  │     │  │  │  │  │  ├─ performance.py
│  │     │  │  │  │  │  ├─ performance_timeline.py
│  │     │  │  │  │  │  ├─ preload.py
│  │     │  │  │  │  │  ├─ profiler.py
│  │     │  │  │  │  │  ├─ pwa.py
│  │     │  │  │  │  │  ├─ py.typed
│  │     │  │  │  │  │  ├─ runtime.py
│  │     │  │  │  │  │  ├─ schema.py
│  │     │  │  │  │  │  ├─ security.py
│  │     │  │  │  │  │  ├─ service_worker.py
│  │     │  │  │  │  │  ├─ storage.py
│  │     │  │  │  │  │  ├─ system_info.py
│  │     │  │  │  │  │  ├─ target.py
│  │     │  │  │  │  │  ├─ tethering.py
│  │     │  │  │  │  │  ├─ tracing.py
│  │     │  │  │  │  │  ├─ util.py
│  │     │  │  │  │  │  ├─ web_audio.py
│  │     │  │  │  │  │  ├─ web_authn.py
│  │     │  │  │  │  │  ├─ __init__.py
│  │     │  │  │  │  │  └─ __pycache__
│  │     │  │  │  │  │     ├─ accessibility.cpython-311.pyc
│  │     │  │  │  │  │     ├─ animation.cpython-311.pyc
│  │     │  │  │  │  │     ├─ audits.cpython-311.pyc
│  │     │  │  │  │  │     ├─ autofill.cpython-311.pyc
│  │     │  │  │  │  │     ├─ background_service.cpython-311.pyc
│  │     │  │  │  │  │     ├─ bluetooth_emulation.cpython-311.pyc
│  │     │  │  │  │  │     ├─ browser.cpython-311.pyc
│  │     │  │  │  │  │     ├─ cache_storage.cpython-311.pyc
│  │     │  │  │  │  │     ├─ cast.cpython-311.pyc
│  │     │  │  │  │  │     ├─ console.cpython-311.pyc
│  │     │  │  │  │  │     ├─ css.cpython-311.pyc
│  │     │  │  │  │  │     ├─ debugger.cpython-311.pyc
│  │     │  │  │  │  │     ├─ device_access.cpython-311.pyc
│  │     │  │  │  │  │     ├─ device_orientation.cpython-311.pyc
│  │     │  │  │  │  │     ├─ dom.cpython-311.pyc
│  │     │  │  │  │  │     ├─ dom_debugger.cpython-311.pyc
│  │     │  │  │  │  │     ├─ dom_snapshot.cpython-311.pyc
│  │     │  │  │  │  │     ├─ dom_storage.cpython-311.pyc
│  │     │  │  │  │  │     ├─ emulation.cpython-311.pyc
│  │     │  │  │  │  │     ├─ event_breakpoints.cpython-311.pyc
│  │     │  │  │  │  │     ├─ extensions.cpython-311.pyc
│  │     │  │  │  │  │     ├─ fed_cm.cpython-311.pyc
│  │     │  │  │  │  │     ├─ fetch.cpython-311.pyc
│  │     │  │  │  │  │     ├─ file_system.cpython-311.pyc
│  │     │  │  │  │  │     ├─ headless_experimental.cpython-311.pyc
│  │     │  │  │  │  │     ├─ heap_profiler.cpython-311.pyc
│  │     │  │  │  │  │     ├─ indexed_db.cpython-311.pyc
│  │     │  │  │  │  │     ├─ input_.cpython-311.pyc
│  │     │  │  │  │  │     ├─ inspector.cpython-311.pyc
│  │     │  │  │  │  │     ├─ io.cpython-311.pyc
│  │     │  │  │  │  │     ├─ layer_tree.cpython-311.pyc
│  │     │  │  │  │  │     ├─ log.cpython-311.pyc
│  │     │  │  │  │  │     ├─ media.cpython-311.pyc
│  │     │  │  │  │  │     ├─ memory.cpython-311.pyc
│  │     │  │  │  │  │     ├─ network.cpython-311.pyc
│  │     │  │  │  │  │     ├─ overlay.cpython-311.pyc
│  │     │  │  │  │  │     ├─ page.cpython-311.pyc
│  │     │  │  │  │  │     ├─ performance.cpython-311.pyc
│  │     │  │  │  │  │     ├─ performance_timeline.cpython-311.pyc
│  │     │  │  │  │  │     ├─ preload.cpython-311.pyc
│  │     │  │  │  │  │     ├─ profiler.cpython-311.pyc
│  │     │  │  │  │  │     ├─ pwa.cpython-311.pyc
│  │     │  │  │  │  │     ├─ runtime.cpython-311.pyc
│  │     │  │  │  │  │     ├─ schema.cpython-311.pyc
│  │     │  │  │  │  │     ├─ security.cpython-311.pyc
│  │     │  │  │  │  │     ├─ service_worker.cpython-311.pyc
│  │     │  │  │  │  │     ├─ storage.cpython-311.pyc
│  │     │  │  │  │  │     ├─ system_info.cpython-311.pyc
│  │     │  │  │  │  │     ├─ target.cpython-311.pyc
│  │     │  │  │  │  │     ├─ tethering.cpython-311.pyc
│  │     │  │  │  │  │     ├─ tracing.cpython-311.pyc
│  │     │  │  │  │  │     ├─ util.cpython-311.pyc
│  │     │  │  │  │  │     ├─ web_audio.cpython-311.pyc
│  │     │  │  │  │  │     ├─ web_authn.cpython-311.pyc
│  │     │  │  │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  │  │  ├─ v137
│  │     │  │  │  │  │  ├─ accessibility.py
│  │     │  │  │  │  │  ├─ animation.py
│  │     │  │  │  │  │  ├─ audits.py
│  │     │  │  │  │  │  ├─ autofill.py
│  │     │  │  │  │  │  ├─ background_service.py
│  │     │  │  │  │  │  ├─ bluetooth_emulation.py
│  │     │  │  │  │  │  ├─ browser.py
│  │     │  │  │  │  │  ├─ cache_storage.py
│  │     │  │  │  │  │  ├─ cast.py
│  │     │  │  │  │  │  ├─ console.py
│  │     │  │  │  │  │  ├─ css.py
│  │     │  │  │  │  │  ├─ debugger.py
│  │     │  │  │  │  │  ├─ device_access.py
│  │     │  │  │  │  │  ├─ device_orientation.py
│  │     │  │  │  │  │  ├─ dom.py
│  │     │  │  │  │  │  ├─ dom_debugger.py
│  │     │  │  │  │  │  ├─ dom_snapshot.py
│  │     │  │  │  │  │  ├─ dom_storage.py
│  │     │  │  │  │  │  ├─ emulation.py
│  │     │  │  │  │  │  ├─ event_breakpoints.py
│  │     │  │  │  │  │  ├─ extensions.py
│  │     │  │  │  │  │  ├─ fed_cm.py
│  │     │  │  │  │  │  ├─ fetch.py
│  │     │  │  │  │  │  ├─ file_system.py
│  │     │  │  │  │  │  ├─ headless_experimental.py
│  │     │  │  │  │  │  ├─ heap_profiler.py
│  │     │  │  │  │  │  ├─ indexed_db.py
│  │     │  │  │  │  │  ├─ input_.py
│  │     │  │  │  │  │  ├─ inspector.py
│  │     │  │  │  │  │  ├─ io.py
│  │     │  │  │  │  │  ├─ layer_tree.py
│  │     │  │  │  │  │  ├─ log.py
│  │     │  │  │  │  │  ├─ media.py
│  │     │  │  │  │  │  ├─ memory.py
│  │     │  │  │  │  │  ├─ network.py
│  │     │  │  │  │  │  ├─ overlay.py
│  │     │  │  │  │  │  ├─ page.py
│  │     │  │  │  │  │  ├─ performance.py
│  │     │  │  │  │  │  ├─ performance_timeline.py
│  │     │  │  │  │  │  ├─ preload.py
│  │     │  │  │  │  │  ├─ profiler.py
│  │     │  │  │  │  │  ├─ pwa.py
│  │     │  │  │  │  │  ├─ py.typed
│  │     │  │  │  │  │  ├─ runtime.py
│  │     │  │  │  │  │  ├─ schema.py
│  │     │  │  │  │  │  ├─ security.py
│  │     │  │  │  │  │  ├─ service_worker.py
│  │     │  │  │  │  │  ├─ storage.py
│  │     │  │  │  │  │  ├─ system_info.py
│  │     │  │  │  │  │  ├─ target.py
│  │     │  │  │  │  │  ├─ tethering.py
│  │     │  │  │  │  │  ├─ tracing.py
│  │     │  │  │  │  │  ├─ util.py
│  │     │  │  │  │  │  ├─ web_audio.py
│  │     │  │  │  │  │  ├─ web_authn.py
│  │     │  │  │  │  │  ├─ __init__.py
│  │     │  │  │  │  │  └─ __pycache__
│  │     │  │  │  │  │     ├─ accessibility.cpython-311.pyc
│  │     │  │  │  │  │     ├─ animation.cpython-311.pyc
│  │     │  │  │  │  │     ├─ audits.cpython-311.pyc
│  │     │  │  │  │  │     ├─ autofill.cpython-311.pyc
│  │     │  │  │  │  │     ├─ background_service.cpython-311.pyc
│  │     │  │  │  │  │     ├─ bluetooth_emulation.cpython-311.pyc
│  │     │  │  │  │  │     ├─ browser.cpython-311.pyc
│  │     │  │  │  │  │     ├─ cache_storage.cpython-311.pyc
│  │     │  │  │  │  │     ├─ cast.cpython-311.pyc
│  │     │  │  │  │  │     ├─ console.cpython-311.pyc
│  │     │  │  │  │  │     ├─ css.cpython-311.pyc
│  │     │  │  │  │  │     ├─ debugger.cpython-311.pyc
│  │     │  │  │  │  │     ├─ device_access.cpython-311.pyc
│  │     │  │  │  │  │     ├─ device_orientation.cpython-311.pyc
│  │     │  │  │  │  │     ├─ dom.cpython-311.pyc
│  │     │  │  │  │  │     ├─ dom_debugger.cpython-311.pyc
│  │     │  │  │  │  │     ├─ dom_snapshot.cpython-311.pyc
│  │     │  │  │  │  │     ├─ dom_storage.cpython-311.pyc
│  │     │  │  │  │  │     ├─ emulation.cpython-311.pyc
│  │     │  │  │  │  │     ├─ event_breakpoints.cpython-311.pyc
│  │     │  │  │  │  │     ├─ extensions.cpython-311.pyc
│  │     │  │  │  │  │     ├─ fed_cm.cpython-311.pyc
│  │     │  │  │  │  │     ├─ fetch.cpython-311.pyc
│  │     │  │  │  │  │     ├─ file_system.cpython-311.pyc
│  │     │  │  │  │  │     ├─ headless_experimental.cpython-311.pyc
│  │     │  │  │  │  │     ├─ heap_profiler.cpython-311.pyc
│  │     │  │  │  │  │     ├─ indexed_db.cpython-311.pyc
│  │     │  │  │  │  │     ├─ input_.cpython-311.pyc
│  │     │  │  │  │  │     ├─ inspector.cpython-311.pyc
│  │     │  │  │  │  │     ├─ io.cpython-311.pyc
│  │     │  │  │  │  │     ├─ layer_tree.cpython-311.pyc
│  │     │  │  │  │  │     ├─ log.cpython-311.pyc
│  │     │  │  │  │  │     ├─ media.cpython-311.pyc
│  │     │  │  │  │  │     ├─ memory.cpython-311.pyc
│  │     │  │  │  │  │     ├─ network.cpython-311.pyc
│  │     │  │  │  │  │     ├─ overlay.cpython-311.pyc
│  │     │  │  │  │  │     ├─ page.cpython-311.pyc
│  │     │  │  │  │  │     ├─ performance.cpython-311.pyc
│  │     │  │  │  │  │     ├─ performance_timeline.cpython-311.pyc
│  │     │  │  │  │  │     ├─ preload.cpython-311.pyc
│  │     │  │  │  │  │     ├─ profiler.cpython-311.pyc
│  │     │  │  │  │  │     ├─ pwa.cpython-311.pyc
│  │     │  │  │  │  │     ├─ runtime.cpython-311.pyc
│  │     │  │  │  │  │     ├─ schema.cpython-311.pyc
│  │     │  │  │  │  │     ├─ security.cpython-311.pyc
│  │     │  │  │  │  │     ├─ service_worker.cpython-311.pyc
│  │     │  │  │  │  │     ├─ storage.cpython-311.pyc
│  │     │  │  │  │  │     ├─ system_info.cpython-311.pyc
│  │     │  │  │  │  │     ├─ target.cpython-311.pyc
│  │     │  │  │  │  │     ├─ tethering.cpython-311.pyc
│  │     │  │  │  │  │     ├─ tracing.cpython-311.pyc
│  │     │  │  │  │  │     ├─ util.cpython-311.pyc
│  │     │  │  │  │  │     ├─ web_audio.cpython-311.pyc
│  │     │  │  │  │  │     ├─ web_authn.cpython-311.pyc
│  │     │  │  │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  │  │  └─ v138
│  │     │  │  │  │     ├─ accessibility.py
│  │     │  │  │  │     ├─ animation.py
│  │     │  │  │  │     ├─ audits.py
│  │     │  │  │  │     ├─ autofill.py
│  │     │  │  │  │     ├─ background_service.py
│  │     │  │  │  │     ├─ bluetooth_emulation.py
│  │     │  │  │  │     ├─ browser.py
│  │     │  │  │  │     ├─ cache_storage.py
│  │     │  │  │  │     ├─ cast.py
│  │     │  │  │  │     ├─ console.py
│  │     │  │  │  │     ├─ css.py
│  │     │  │  │  │     ├─ debugger.py
│  │     │  │  │  │     ├─ device_access.py
│  │     │  │  │  │     ├─ device_orientation.py
│  │     │  │  │  │     ├─ dom.py
│  │     │  │  │  │     ├─ dom_debugger.py
│  │     │  │  │  │     ├─ dom_snapshot.py
│  │     │  │  │  │     ├─ dom_storage.py
│  │     │  │  │  │     ├─ emulation.py
│  │     │  │  │  │     ├─ event_breakpoints.py
│  │     │  │  │  │     ├─ extensions.py
│  │     │  │  │  │     ├─ fed_cm.py
│  │     │  │  │  │     ├─ fetch.py
│  │     │  │  │  │     ├─ file_system.py
│  │     │  │  │  │     ├─ headless_experimental.py
│  │     │  │  │  │     ├─ heap_profiler.py
│  │     │  │  │  │     ├─ indexed_db.py
│  │     │  │  │  │     ├─ input_.py
│  │     │  │  │  │     ├─ inspector.py
│  │     │  │  │  │     ├─ io.py
│  │     │  │  │  │     ├─ layer_tree.py
│  │     │  │  │  │     ├─ log.py
│  │     │  │  │  │     ├─ media.py
│  │     │  │  │  │     ├─ memory.py
│  │     │  │  │  │     ├─ network.py
│  │     │  │  │  │     ├─ overlay.py
│  │     │  │  │  │     ├─ page.py
│  │     │  │  │  │     ├─ performance.py
│  │     │  │  │  │     ├─ performance_timeline.py
│  │     │  │  │  │     ├─ preload.py
│  │     │  │  │  │     ├─ profiler.py
│  │     │  │  │  │     ├─ pwa.py
│  │     │  │  │  │     ├─ py.typed
│  │     │  │  │  │     ├─ runtime.py
│  │     │  │  │  │     ├─ schema.py
│  │     │  │  │  │     ├─ security.py
│  │     │  │  │  │     ├─ service_worker.py
│  │     │  │  │  │     ├─ storage.py
│  │     │  │  │  │     ├─ system_info.py
│  │     │  │  │  │     ├─ target.py
│  │     │  │  │  │     ├─ tethering.py
│  │     │  │  │  │     ├─ tracing.py
│  │     │  │  │  │     ├─ util.py
│  │     │  │  │  │     ├─ web_audio.py
│  │     │  │  │  │     ├─ web_authn.py
│  │     │  │  │  │     ├─ __init__.py
│  │     │  │  │  │     └─ __pycache__
│  │     │  │  │  │        ├─ accessibility.cpython-311.pyc
│  │     │  │  │  │        ├─ animation.cpython-311.pyc
│  │     │  │  │  │        ├─ audits.cpython-311.pyc
│  │     │  │  │  │        ├─ autofill.cpython-311.pyc
│  │     │  │  │  │        ├─ background_service.cpython-311.pyc
│  │     │  │  │  │        ├─ bluetooth_emulation.cpython-311.pyc
│  │     │  │  │  │        ├─ browser.cpython-311.pyc
│  │     │  │  │  │        ├─ cache_storage.cpython-311.pyc
│  │     │  │  │  │        ├─ cast.cpython-311.pyc
│  │     │  │  │  │        ├─ console.cpython-311.pyc
│  │     │  │  │  │        ├─ css.cpython-311.pyc
│  │     │  │  │  │        ├─ debugger.cpython-311.pyc
│  │     │  │  │  │        ├─ device_access.cpython-311.pyc
│  │     │  │  │  │        ├─ device_orientation.cpython-311.pyc
│  │     │  │  │  │        ├─ dom.cpython-311.pyc
│  │     │  │  │  │        ├─ dom_debugger.cpython-311.pyc
│  │     │  │  │  │        ├─ dom_snapshot.cpython-311.pyc
│  │     │  │  │  │        ├─ dom_storage.cpython-311.pyc
│  │     │  │  │  │        ├─ emulation.cpython-311.pyc
│  │     │  │  │  │        ├─ event_breakpoints.cpython-311.pyc
│  │     │  │  │  │        ├─ extensions.cpython-311.pyc
│  │     │  │  │  │        ├─ fed_cm.cpython-311.pyc
│  │     │  │  │  │        ├─ fetch.cpython-311.pyc
│  │     │  │  │  │        ├─ file_system.cpython-311.pyc
│  │     │  │  │  │        ├─ headless_experimental.cpython-311.pyc
│  │     │  │  │  │        ├─ heap_profiler.cpython-311.pyc
│  │     │  │  │  │        ├─ indexed_db.cpython-311.pyc
│  │     │  │  │  │        ├─ input_.cpython-311.pyc
│  │     │  │  │  │        ├─ inspector.cpython-311.pyc
│  │     │  │  │  │        ├─ io.cpython-311.pyc
│  │     │  │  │  │        ├─ layer_tree.cpython-311.pyc
│  │     │  │  │  │        ├─ log.cpython-311.pyc
│  │     │  │  │  │        ├─ media.cpython-311.pyc
│  │     │  │  │  │        ├─ memory.cpython-311.pyc
│  │     │  │  │  │        ├─ network.cpython-311.pyc
│  │     │  │  │  │        ├─ overlay.cpython-311.pyc
│  │     │  │  │  │        ├─ page.cpython-311.pyc
│  │     │  │  │  │        ├─ performance.cpython-311.pyc
│  │     │  │  │  │        ├─ performance_timeline.cpython-311.pyc
│  │     │  │  │  │        ├─ preload.cpython-311.pyc
│  │     │  │  │  │        ├─ profiler.cpython-311.pyc
│  │     │  │  │  │        ├─ pwa.cpython-311.pyc
│  │     │  │  │  │        ├─ runtime.cpython-311.pyc
│  │     │  │  │  │        ├─ schema.cpython-311.pyc
│  │     │  │  │  │        ├─ security.cpython-311.pyc
│  │     │  │  │  │        ├─ service_worker.cpython-311.pyc
│  │     │  │  │  │        ├─ storage.cpython-311.pyc
│  │     │  │  │  │        ├─ system_info.cpython-311.pyc
│  │     │  │  │  │        ├─ target.cpython-311.pyc
│  │     │  │  │  │        ├─ tethering.cpython-311.pyc
│  │     │  │  │  │        ├─ tracing.cpython-311.pyc
│  │     │  │  │  │        ├─ util.cpython-311.pyc
│  │     │  │  │  │        ├─ web_audio.cpython-311.pyc
│  │     │  │  │  │        ├─ web_authn.cpython-311.pyc
│  │     │  │  │  │        └─ __init__.cpython-311.pyc
│  │     │  │  │  ├─ driver_finder.py
│  │     │  │  │  ├─ fedcm
│  │     │  │  │  │  ├─ account.py
│  │     │  │  │  │  ├─ dialog.py
│  │     │  │  │  │  ├─ __init__.py
│  │     │  │  │  │  └─ __pycache__
│  │     │  │  │  │     ├─ account.cpython-311.pyc
│  │     │  │  │  │     ├─ dialog.cpython-311.pyc
│  │     │  │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  │  ├─ keys.py
│  │     │  │  │  ├─ linux
│  │     │  │  │  │  └─ selenium-manager
│  │     │  │  │  ├─ log.py
│  │     │  │  │  ├─ macos
│  │     │  │  │  │  └─ selenium-manager
│  │     │  │  │  ├─ mutation-listener.js
│  │     │  │  │  ├─ options.py
│  │     │  │  │  ├─ print_page_options.py
│  │     │  │  │  ├─ proxy.py
│  │     │  │  │  ├─ selenium_manager.py
│  │     │  │  │  ├─ service.py
│  │     │  │  │  ├─ timeouts.py
│  │     │  │  │  ├─ utils.py
│  │     │  │  │  ├─ virtual_authenticator.py
│  │     │  │  │  ├─ window.py
│  │     │  │  │  ├─ windows
│  │     │  │  │  │  └─ selenium-manager.exe
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ action_chains.cpython-311.pyc
│  │     │  │  │     ├─ alert.cpython-311.pyc
│  │     │  │  │     ├─ by.cpython-311.pyc
│  │     │  │  │     ├─ desired_capabilities.cpython-311.pyc
│  │     │  │  │     ├─ driver_finder.cpython-311.pyc
│  │     │  │  │     ├─ keys.cpython-311.pyc
│  │     │  │  │     ├─ log.cpython-311.pyc
│  │     │  │  │     ├─ options.cpython-311.pyc
│  │     │  │  │     ├─ print_page_options.cpython-311.pyc
│  │     │  │  │     ├─ proxy.cpython-311.pyc
│  │     │  │  │     ├─ selenium_manager.cpython-311.pyc
│  │     │  │  │     ├─ service.cpython-311.pyc
│  │     │  │  │     ├─ timeouts.cpython-311.pyc
│  │     │  │  │     ├─ utils.cpython-311.pyc
│  │     │  │  │     ├─ virtual_authenticator.cpython-311.pyc
│  │     │  │  │     ├─ window.cpython-311.pyc
│  │     │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  ├─ edge
│  │     │  │  │  ├─ options.py
│  │     │  │  │  ├─ remote_connection.py
│  │     │  │  │  ├─ service.py
│  │     │  │  │  ├─ webdriver.py
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ options.cpython-311.pyc
│  │     │  │  │     ├─ remote_connection.cpython-311.pyc
│  │     │  │  │     ├─ service.cpython-311.pyc
│  │     │  │  │     ├─ webdriver.cpython-311.pyc
│  │     │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  ├─ firefox
│  │     │  │  │  ├─ firefox_binary.py
│  │     │  │  │  ├─ firefox_profile.py
│  │     │  │  │  ├─ options.py
│  │     │  │  │  ├─ remote_connection.py
│  │     │  │  │  ├─ service.py
│  │     │  │  │  ├─ webdriver.py
│  │     │  │  │  ├─ webdriver_prefs.json
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ firefox_binary.cpython-311.pyc
│  │     │  │  │     ├─ firefox_profile.cpython-311.pyc
│  │     │  │  │     ├─ options.cpython-311.pyc
│  │     │  │  │     ├─ remote_connection.cpython-311.pyc
│  │     │  │  │     ├─ service.cpython-311.pyc
│  │     │  │  │     ├─ webdriver.cpython-311.pyc
│  │     │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  ├─ ie
│  │     │  │  │  ├─ options.py
│  │     │  │  │  ├─ service.py
│  │     │  │  │  ├─ webdriver.py
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ options.cpython-311.pyc
│  │     │  │  │     ├─ service.cpython-311.pyc
│  │     │  │  │     ├─ webdriver.cpython-311.pyc
│  │     │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  ├─ remote
│  │     │  │  │  ├─ bidi_connection.py
│  │     │  │  │  ├─ client_config.py
│  │     │  │  │  ├─ command.py
│  │     │  │  │  ├─ errorhandler.py
│  │     │  │  │  ├─ fedcm.py
│  │     │  │  │  ├─ file_detector.py
│  │     │  │  │  ├─ findElements.js
│  │     │  │  │  ├─ getAttribute.js
│  │     │  │  │  ├─ isDisplayed.js
│  │     │  │  │  ├─ locator_converter.py
│  │     │  │  │  ├─ mobile.py
│  │     │  │  │  ├─ remote_connection.py
│  │     │  │  │  ├─ script_key.py
│  │     │  │  │  ├─ server.py
│  │     │  │  │  ├─ shadowroot.py
│  │     │  │  │  ├─ switch_to.py
│  │     │  │  │  ├─ utils.py
│  │     │  │  │  ├─ webdriver.py
│  │     │  │  │  ├─ webelement.py
│  │     │  │  │  ├─ websocket_connection.py
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ bidi_connection.cpython-311.pyc
│  │     │  │  │     ├─ client_config.cpython-311.pyc
│  │     │  │  │     ├─ command.cpython-311.pyc
│  │     │  │  │     ├─ errorhandler.cpython-311.pyc
│  │     │  │  │     ├─ fedcm.cpython-311.pyc
│  │     │  │  │     ├─ file_detector.cpython-311.pyc
│  │     │  │  │     ├─ locator_converter.cpython-311.pyc
│  │     │  │  │     ├─ mobile.cpython-311.pyc
│  │     │  │  │     ├─ remote_connection.cpython-311.pyc
│  │     │  │  │     ├─ script_key.cpython-311.pyc
│  │     │  │  │     ├─ server.cpython-311.pyc
│  │     │  │  │     ├─ shadowroot.cpython-311.pyc
│  │     │  │  │     ├─ switch_to.cpython-311.pyc
│  │     │  │  │     ├─ utils.cpython-311.pyc
│  │     │  │  │     ├─ webdriver.cpython-311.pyc
│  │     │  │  │     ├─ webelement.cpython-311.pyc
│  │     │  │  │     ├─ websocket_connection.cpython-311.pyc
│  │     │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  ├─ safari
│  │     │  │  │  ├─ options.py
│  │     │  │  │  ├─ permissions.py
│  │     │  │  │  ├─ remote_connection.py
│  │     │  │  │  ├─ service.py
│  │     │  │  │  ├─ webdriver.py
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ options.cpython-311.pyc
│  │     │  │  │     ├─ permissions.cpython-311.pyc
│  │     │  │  │     ├─ remote_connection.cpython-311.pyc
│  │     │  │  │     ├─ service.cpython-311.pyc
│  │     │  │  │     ├─ webdriver.cpython-311.pyc
│  │     │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  ├─ support
│  │     │  │  │  ├─ abstract_event_listener.py
│  │     │  │  │  ├─ color.py
│  │     │  │  │  ├─ events.py
│  │     │  │  │  ├─ event_firing_webdriver.py
│  │     │  │  │  ├─ expected_conditions.py
│  │     │  │  │  ├─ relative_locator.py
│  │     │  │  │  ├─ select.py
│  │     │  │  │  ├─ ui.py
│  │     │  │  │  ├─ wait.py
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ abstract_event_listener.cpython-311.pyc
│  │     │  │  │     ├─ color.cpython-311.pyc
│  │     │  │  │     ├─ events.cpython-311.pyc
│  │     │  │  │     ├─ event_firing_webdriver.cpython-311.pyc
│  │     │  │  │     ├─ expected_conditions.cpython-311.pyc
│  │     │  │  │     ├─ relative_locator.cpython-311.pyc
│  │     │  │  │     ├─ select.cpython-311.pyc
│  │     │  │  │     ├─ ui.cpython-311.pyc
│  │     │  │  │     ├─ wait.cpython-311.pyc
│  │     │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  ├─ webkitgtk
│  │     │  │  │  ├─ options.py
│  │     │  │  │  ├─ service.py
│  │     │  │  │  ├─ webdriver.py
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ options.cpython-311.pyc
│  │     │  │  │     ├─ service.cpython-311.pyc
│  │     │  │  │     ├─ webdriver.cpython-311.pyc
│  │     │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  ├─ wpewebkit
│  │     │  │  │  ├─ options.py
│  │     │  │  │  ├─ service.py
│  │     │  │  │  ├─ webdriver.py
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ options.cpython-311.pyc
│  │     │  │  │     ├─ service.cpython-311.pyc
│  │     │  │  │     ├─ webdriver.cpython-311.pyc
│  │     │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  ├─ __init__.py
│  │     │  │  └─ __pycache__
│  │     │  │     └─ __init__.cpython-311.pyc
│  │     │  ├─ __init__.py
│  │     │  └─ __pycache__
│  │     │     ├─ types.cpython-311.pyc
│  │     │     └─ __init__.cpython-311.pyc
│  │     ├─ selenium-4.34.2.dist-info
│  │     │  ├─ INSTALLER
│  │     │  ├─ LICENSE
│  │     │  ├─ METADATA
│  │     │  ├─ RECORD
│  │     │  ├─ REQUESTED
│  │     │  └─ WHEEL
│  │     ├─ setuptools
│  │     │  ├─ archive_util.py
│  │     │  ├─ build_meta.py
│  │     │  ├─ cli-32.exe
│  │     │  ├─ cli-64.exe
│  │     │  ├─ cli-arm64.exe
│  │     │  ├─ cli.exe
│  │     │  ├─ command
│  │     │  │  ├─ alias.py
│  │     │  │  ├─ bdist_egg.py
│  │     │  │  ├─ bdist_rpm.py
│  │     │  │  ├─ build.py
│  │     │  │  ├─ build_clib.py
│  │     │  │  ├─ build_ext.py
│  │     │  │  ├─ build_py.py
│  │     │  │  ├─ develop.py
│  │     │  │  ├─ dist_info.py
│  │     │  │  ├─ easy_install.py
│  │     │  │  ├─ editable_wheel.py
│  │     │  │  ├─ egg_info.py
│  │     │  │  ├─ install.py
│  │     │  │  ├─ install_egg_info.py
│  │     │  │  ├─ install_lib.py
│  │     │  │  ├─ install_scripts.py
│  │     │  │  ├─ launcher manifest.xml
│  │     │  │  ├─ py36compat.py
│  │     │  │  ├─ register.py
│  │     │  │  ├─ rotate.py
│  │     │  │  ├─ saveopts.py
│  │     │  │  ├─ sdist.py
│  │     │  │  ├─ setopt.py
│  │     │  │  ├─ test.py
│  │     │  │  ├─ upload.py
│  │     │  │  ├─ upload_docs.py
│  │     │  │  ├─ __init__.py
│  │     │  │  └─ __pycache__
│  │     │  │     ├─ alias.cpython-311.pyc
│  │     │  │     ├─ bdist_egg.cpython-311.pyc
│  │     │  │     ├─ bdist_rpm.cpython-311.pyc
│  │     │  │     ├─ build.cpython-311.pyc
│  │     │  │     ├─ build_clib.cpython-311.pyc
│  │     │  │     ├─ build_ext.cpython-311.pyc
│  │     │  │     ├─ build_py.cpython-311.pyc
│  │     │  │     ├─ develop.cpython-311.pyc
│  │     │  │     ├─ dist_info.cpython-311.pyc
│  │     │  │     ├─ easy_install.cpython-311.pyc
│  │     │  │     ├─ editable_wheel.cpython-311.pyc
│  │     │  │     ├─ egg_info.cpython-311.pyc
│  │     │  │     ├─ install.cpython-311.pyc
│  │     │  │     ├─ install_egg_info.cpython-311.pyc
│  │     │  │     ├─ install_lib.cpython-311.pyc
│  │     │  │     ├─ install_scripts.cpython-311.pyc
│  │     │  │     ├─ py36compat.cpython-311.pyc
│  │     │  │     ├─ register.cpython-311.pyc
│  │     │  │     ├─ rotate.cpython-311.pyc
│  │     │  │     ├─ saveopts.cpython-311.pyc
│  │     │  │     ├─ sdist.cpython-311.pyc
│  │     │  │     ├─ setopt.cpython-311.pyc
│  │     │  │     ├─ test.cpython-311.pyc
│  │     │  │     ├─ upload.cpython-311.pyc
│  │     │  │     ├─ upload_docs.cpython-311.pyc
│  │     │  │     └─ __init__.cpython-311.pyc
│  │     │  ├─ config
│  │     │  │  ├─ expand.py
│  │     │  │  ├─ pyprojecttoml.py
│  │     │  │  ├─ setupcfg.py
│  │     │  │  ├─ _apply_pyprojecttoml.py
│  │     │  │  ├─ _validate_pyproject
│  │     │  │  │  ├─ error_reporting.py
│  │     │  │  │  ├─ extra_validations.py
│  │     │  │  │  ├─ fastjsonschema_exceptions.py
│  │     │  │  │  ├─ fastjsonschema_validations.py
│  │     │  │  │  ├─ formats.py
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ error_reporting.cpython-311.pyc
│  │     │  │  │     ├─ extra_validations.cpython-311.pyc
│  │     │  │  │     ├─ fastjsonschema_exceptions.cpython-311.pyc
│  │     │  │  │     ├─ fastjsonschema_validations.cpython-311.pyc
│  │     │  │  │     ├─ formats.cpython-311.pyc
│  │     │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  ├─ __init__.py
│  │     │  │  └─ __pycache__
│  │     │  │     ├─ expand.cpython-311.pyc
│  │     │  │     ├─ pyprojecttoml.cpython-311.pyc
│  │     │  │     ├─ setupcfg.cpython-311.pyc
│  │     │  │     ├─ _apply_pyprojecttoml.cpython-311.pyc
│  │     │  │     └─ __init__.cpython-311.pyc
│  │     │  ├─ depends.py
│  │     │  ├─ dep_util.py
│  │     │  ├─ discovery.py
│  │     │  ├─ dist.py
│  │     │  ├─ errors.py
│  │     │  ├─ extension.py
│  │     │  ├─ extern
│  │     │  │  ├─ __init__.py
│  │     │  │  └─ __pycache__
│  │     │  │     └─ __init__.cpython-311.pyc
│  │     │  ├─ glob.py
│  │     │  ├─ gui-32.exe
│  │     │  ├─ gui-64.exe
│  │     │  ├─ gui-arm64.exe
│  │     │  ├─ gui.exe
│  │     │  ├─ installer.py
│  │     │  ├─ launch.py
│  │     │  ├─ logging.py
│  │     │  ├─ monkey.py
│  │     │  ├─ msvc.py
│  │     │  ├─ namespaces.py
│  │     │  ├─ package_index.py
│  │     │  ├─ py34compat.py
│  │     │  ├─ sandbox.py
│  │     │  ├─ script (dev).tmpl
│  │     │  ├─ script.tmpl
│  │     │  ├─ unicode_utils.py
│  │     │  ├─ version.py
│  │     │  ├─ wheel.py
│  │     │  ├─ windows_support.py
│  │     │  ├─ _deprecation_warning.py
│  │     │  ├─ _distutils
│  │     │  │  ├─ archive_util.py
│  │     │  │  ├─ bcppcompiler.py
│  │     │  │  ├─ ccompiler.py
│  │     │  │  ├─ cmd.py
│  │     │  │  ├─ command
│  │     │  │  │  ├─ bdist.py
│  │     │  │  │  ├─ bdist_dumb.py
│  │     │  │  │  ├─ bdist_rpm.py
│  │     │  │  │  ├─ build.py
│  │     │  │  │  ├─ build_clib.py
│  │     │  │  │  ├─ build_ext.py
│  │     │  │  │  ├─ build_py.py
│  │     │  │  │  ├─ build_scripts.py
│  │     │  │  │  ├─ check.py
│  │     │  │  │  ├─ clean.py
│  │     │  │  │  ├─ config.py
│  │     │  │  │  ├─ install.py
│  │     │  │  │  ├─ install_data.py
│  │     │  │  │  ├─ install_egg_info.py
│  │     │  │  │  ├─ install_headers.py
│  │     │  │  │  ├─ install_lib.py
│  │     │  │  │  ├─ install_scripts.py
│  │     │  │  │  ├─ py37compat.py
│  │     │  │  │  ├─ register.py
│  │     │  │  │  ├─ sdist.py
│  │     │  │  │  ├─ upload.py
│  │     │  │  │  ├─ _framework_compat.py
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ bdist.cpython-311.pyc
│  │     │  │  │     ├─ bdist_dumb.cpython-311.pyc
│  │     │  │  │     ├─ bdist_rpm.cpython-311.pyc
│  │     │  │  │     ├─ build.cpython-311.pyc
│  │     │  │  │     ├─ build_clib.cpython-311.pyc
│  │     │  │  │     ├─ build_ext.cpython-311.pyc
│  │     │  │  │     ├─ build_py.cpython-311.pyc
│  │     │  │  │     ├─ build_scripts.cpython-311.pyc
│  │     │  │  │     ├─ check.cpython-311.pyc
│  │     │  │  │     ├─ clean.cpython-311.pyc
│  │     │  │  │     ├─ config.cpython-311.pyc
│  │     │  │  │     ├─ install.cpython-311.pyc
│  │     │  │  │     ├─ install_data.cpython-311.pyc
│  │     │  │  │     ├─ install_egg_info.cpython-311.pyc
│  │     │  │  │     ├─ install_headers.cpython-311.pyc
│  │     │  │  │     ├─ install_lib.cpython-311.pyc
│  │     │  │  │     ├─ install_scripts.cpython-311.pyc
│  │     │  │  │     ├─ py37compat.cpython-311.pyc
│  │     │  │  │     ├─ register.cpython-311.pyc
│  │     │  │  │     ├─ sdist.cpython-311.pyc
│  │     │  │  │     ├─ upload.cpython-311.pyc
│  │     │  │  │     ├─ _framework_compat.cpython-311.pyc
│  │     │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  ├─ config.py
│  │     │  │  ├─ core.py
│  │     │  │  ├─ cygwinccompiler.py
│  │     │  │  ├─ debug.py
│  │     │  │  ├─ dep_util.py
│  │     │  │  ├─ dir_util.py
│  │     │  │  ├─ dist.py
│  │     │  │  ├─ errors.py
│  │     │  │  ├─ extension.py
│  │     │  │  ├─ fancy_getopt.py
│  │     │  │  ├─ filelist.py
│  │     │  │  ├─ file_util.py
│  │     │  │  ├─ log.py
│  │     │  │  ├─ msvc9compiler.py
│  │     │  │  ├─ msvccompiler.py
│  │     │  │  ├─ py38compat.py
│  │     │  │  ├─ py39compat.py
│  │     │  │  ├─ spawn.py
│  │     │  │  ├─ sysconfig.py
│  │     │  │  ├─ text_file.py
│  │     │  │  ├─ unixccompiler.py
│  │     │  │  ├─ util.py
│  │     │  │  ├─ version.py
│  │     │  │  ├─ versionpredicate.py
│  │     │  │  ├─ _collections.py
│  │     │  │  ├─ _functools.py
│  │     │  │  ├─ _macos_compat.py
│  │     │  │  ├─ _msvccompiler.py
│  │     │  │  ├─ __init__.py
│  │     │  │  └─ __pycache__
│  │     │  │     ├─ archive_util.cpython-311.pyc
│  │     │  │     ├─ bcppcompiler.cpython-311.pyc
│  │     │  │     ├─ ccompiler.cpython-311.pyc
│  │     │  │     ├─ cmd.cpython-311.pyc
│  │     │  │     ├─ config.cpython-311.pyc
│  │     │  │     ├─ core.cpython-311.pyc
│  │     │  │     ├─ cygwinccompiler.cpython-311.pyc
│  │     │  │     ├─ debug.cpython-311.pyc
│  │     │  │     ├─ dep_util.cpython-311.pyc
│  │     │  │     ├─ dir_util.cpython-311.pyc
│  │     │  │     ├─ dist.cpython-311.pyc
│  │     │  │     ├─ errors.cpython-311.pyc
│  │     │  │     ├─ extension.cpython-311.pyc
│  │     │  │     ├─ fancy_getopt.cpython-311.pyc
│  │     │  │     ├─ filelist.cpython-311.pyc
│  │     │  │     ├─ file_util.cpython-311.pyc
│  │     │  │     ├─ log.cpython-311.pyc
│  │     │  │     ├─ msvc9compiler.cpython-311.pyc
│  │     │  │     ├─ msvccompiler.cpython-311.pyc
│  │     │  │     ├─ py38compat.cpython-311.pyc
│  │     │  │     ├─ py39compat.cpython-311.pyc
│  │     │  │     ├─ spawn.cpython-311.pyc
│  │     │  │     ├─ sysconfig.cpython-311.pyc
│  │     │  │     ├─ text_file.cpython-311.pyc
│  │     │  │     ├─ unixccompiler.cpython-311.pyc
│  │     │  │     ├─ util.cpython-311.pyc
│  │     │  │     ├─ version.cpython-311.pyc
│  │     │  │     ├─ versionpredicate.cpython-311.pyc
│  │     │  │     ├─ _collections.cpython-311.pyc
│  │     │  │     ├─ _functools.cpython-311.pyc
│  │     │  │     ├─ _macos_compat.cpython-311.pyc
│  │     │  │     ├─ _msvccompiler.cpython-311.pyc
│  │     │  │     └─ __init__.cpython-311.pyc
│  │     │  ├─ _entry_points.py
│  │     │  ├─ _imp.py
│  │     │  ├─ _importlib.py
│  │     │  ├─ _itertools.py
│  │     │  ├─ _path.py
│  │     │  ├─ _reqs.py
│  │     │  ├─ _vendor
│  │     │  │  ├─ importlib_metadata
│  │     │  │  │  ├─ _adapters.py
│  │     │  │  │  ├─ _collections.py
│  │     │  │  │  ├─ _compat.py
│  │     │  │  │  ├─ _functools.py
│  │     │  │  │  ├─ _itertools.py
│  │     │  │  │  ├─ _meta.py
│  │     │  │  │  ├─ _text.py
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ _adapters.cpython-311.pyc
│  │     │  │  │     ├─ _collections.cpython-311.pyc
│  │     │  │  │     ├─ _compat.cpython-311.pyc
│  │     │  │  │     ├─ _functools.cpython-311.pyc
│  │     │  │  │     ├─ _itertools.cpython-311.pyc
│  │     │  │  │     ├─ _meta.cpython-311.pyc
│  │     │  │  │     ├─ _text.cpython-311.pyc
│  │     │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  ├─ importlib_resources
│  │     │  │  │  ├─ abc.py
│  │     │  │  │  ├─ readers.py
│  │     │  │  │  ├─ simple.py
│  │     │  │  │  ├─ _adapters.py
│  │     │  │  │  ├─ _common.py
│  │     │  │  │  ├─ _compat.py
│  │     │  │  │  ├─ _itertools.py
│  │     │  │  │  ├─ _legacy.py
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ abc.cpython-311.pyc
│  │     │  │  │     ├─ readers.cpython-311.pyc
│  │     │  │  │     ├─ simple.cpython-311.pyc
│  │     │  │  │     ├─ _adapters.cpython-311.pyc
│  │     │  │  │     ├─ _common.cpython-311.pyc
│  │     │  │  │     ├─ _compat.cpython-311.pyc
│  │     │  │  │     ├─ _itertools.cpython-311.pyc
│  │     │  │  │     ├─ _legacy.cpython-311.pyc
│  │     │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  ├─ jaraco
│  │     │  │  │  ├─ context.py
│  │     │  │  │  ├─ functools.py
│  │     │  │  │  ├─ text
│  │     │  │  │  │  ├─ __init__.py
│  │     │  │  │  │  └─ __pycache__
│  │     │  │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ context.cpython-311.pyc
│  │     │  │  │     ├─ functools.cpython-311.pyc
│  │     │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  ├─ more_itertools
│  │     │  │  │  ├─ more.py
│  │     │  │  │  ├─ recipes.py
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ more.cpython-311.pyc
│  │     │  │  │     ├─ recipes.cpython-311.pyc
│  │     │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  ├─ ordered_set.py
│  │     │  │  ├─ packaging
│  │     │  │  │  ├─ markers.py
│  │     │  │  │  ├─ requirements.py
│  │     │  │  │  ├─ specifiers.py
│  │     │  │  │  ├─ tags.py
│  │     │  │  │  ├─ utils.py
│  │     │  │  │  ├─ version.py
│  │     │  │  │  ├─ _manylinux.py
│  │     │  │  │  ├─ _musllinux.py
│  │     │  │  │  ├─ _structures.py
│  │     │  │  │  ├─ __about__.py
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ markers.cpython-311.pyc
│  │     │  │  │     ├─ requirements.cpython-311.pyc
│  │     │  │  │     ├─ specifiers.cpython-311.pyc
│  │     │  │  │     ├─ tags.cpython-311.pyc
│  │     │  │  │     ├─ utils.cpython-311.pyc
│  │     │  │  │     ├─ version.cpython-311.pyc
│  │     │  │  │     ├─ _manylinux.cpython-311.pyc
│  │     │  │  │     ├─ _musllinux.cpython-311.pyc
│  │     │  │  │     ├─ _structures.cpython-311.pyc
│  │     │  │  │     ├─ __about__.cpython-311.pyc
│  │     │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  ├─ pyparsing
│  │     │  │  │  ├─ actions.py
│  │     │  │  │  ├─ common.py
│  │     │  │  │  ├─ core.py
│  │     │  │  │  ├─ diagram
│  │     │  │  │  │  ├─ __init__.py
│  │     │  │  │  │  └─ __pycache__
│  │     │  │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  │  ├─ exceptions.py
│  │     │  │  │  ├─ helpers.py
│  │     │  │  │  ├─ results.py
│  │     │  │  │  ├─ testing.py
│  │     │  │  │  ├─ unicode.py
│  │     │  │  │  ├─ util.py
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ actions.cpython-311.pyc
│  │     │  │  │     ├─ common.cpython-311.pyc
│  │     │  │  │     ├─ core.cpython-311.pyc
│  │     │  │  │     ├─ exceptions.cpython-311.pyc
│  │     │  │  │     ├─ helpers.cpython-311.pyc
│  │     │  │  │     ├─ results.cpython-311.pyc
│  │     │  │  │     ├─ testing.cpython-311.pyc
│  │     │  │  │     ├─ unicode.cpython-311.pyc
│  │     │  │  │     ├─ util.cpython-311.pyc
│  │     │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  ├─ tomli
│  │     │  │  │  ├─ _parser.py
│  │     │  │  │  ├─ _re.py
│  │     │  │  │  ├─ _types.py
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ _parser.cpython-311.pyc
│  │     │  │  │     ├─ _re.cpython-311.pyc
│  │     │  │  │     ├─ _types.cpython-311.pyc
│  │     │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  ├─ typing_extensions.py
│  │     │  │  ├─ zipp.py
│  │     │  │  ├─ __init__.py
│  │     │  │  └─ __pycache__
│  │     │  │     ├─ ordered_set.cpython-311.pyc
│  │     │  │     ├─ typing_extensions.cpython-311.pyc
│  │     │  │     ├─ zipp.cpython-311.pyc
│  │     │  │     └─ __init__.cpython-311.pyc
│  │     │  ├─ __init__.py
│  │     │  └─ __pycache__
│  │     │     ├─ archive_util.cpython-311.pyc
│  │     │     ├─ build_meta.cpython-311.pyc
│  │     │     ├─ depends.cpython-311.pyc
│  │     │     ├─ dep_util.cpython-311.pyc
│  │     │     ├─ discovery.cpython-311.pyc
│  │     │     ├─ dist.cpython-311.pyc
│  │     │     ├─ errors.cpython-311.pyc
│  │     │     ├─ extension.cpython-311.pyc
│  │     │     ├─ glob.cpython-311.pyc
│  │     │     ├─ installer.cpython-311.pyc
│  │     │     ├─ launch.cpython-311.pyc
│  │     │     ├─ logging.cpython-311.pyc
│  │     │     ├─ monkey.cpython-311.pyc
│  │     │     ├─ msvc.cpython-311.pyc
│  │     │     ├─ namespaces.cpython-311.pyc
│  │     │     ├─ package_index.cpython-311.pyc
│  │     │     ├─ py34compat.cpython-311.pyc
│  │     │     ├─ sandbox.cpython-311.pyc
│  │     │     ├─ unicode_utils.cpython-311.pyc
│  │     │     ├─ version.cpython-311.pyc
│  │     │     ├─ wheel.cpython-311.pyc
│  │     │     ├─ windows_support.cpython-311.pyc
│  │     │     ├─ _deprecation_warning.cpython-311.pyc
│  │     │     ├─ _entry_points.cpython-311.pyc
│  │     │     ├─ _imp.cpython-311.pyc
│  │     │     ├─ _importlib.cpython-311.pyc
│  │     │     ├─ _itertools.cpython-311.pyc
│  │     │     ├─ _path.cpython-311.pyc
│  │     │     ├─ _reqs.cpython-311.pyc
│  │     │     └─ __init__.cpython-311.pyc
│  │     ├─ setuptools-65.5.0.dist-info
│  │     │  ├─ entry_points.txt
│  │     │  ├─ INSTALLER
│  │     │  ├─ LICENSE
│  │     │  ├─ METADATA
│  │     │  ├─ RECORD
│  │     │  ├─ REQUESTED
│  │     │  ├─ top_level.txt
│  │     │  └─ WHEEL
│  │     ├─ sniffio
│  │     │  ├─ py.typed
│  │     │  ├─ _impl.py
│  │     │  ├─ _tests
│  │     │  │  ├─ test_sniffio.py
│  │     │  │  ├─ __init__.py
│  │     │  │  └─ __pycache__
│  │     │  │     ├─ test_sniffio.cpython-311.pyc
│  │     │  │     └─ __init__.cpython-311.pyc
│  │     │  ├─ _version.py
│  │     │  ├─ __init__.py
│  │     │  └─ __pycache__
│  │     │     ├─ _impl.cpython-311.pyc
│  │     │     ├─ _version.cpython-311.pyc
│  │     │     └─ __init__.cpython-311.pyc
│  │     ├─ sniffio-1.3.1.dist-info
│  │     │  ├─ INSTALLER
│  │     │  ├─ LICENSE
│  │     │  ├─ LICENSE.APACHE2
│  │     │  ├─ LICENSE.MIT
│  │     │  ├─ METADATA
│  │     │  ├─ RECORD
│  │     │  ├─ top_level.txt
│  │     │  └─ WHEEL
│  │     ├─ socks.py
│  │     ├─ sockshandler.py
│  │     ├─ sortedcontainers
│  │     │  ├─ sorteddict.py
│  │     │  ├─ sortedlist.py
│  │     │  ├─ sortedset.py
│  │     │  ├─ __init__.py
│  │     │  └─ __pycache__
│  │     │     ├─ sorteddict.cpython-311.pyc
│  │     │     ├─ sortedlist.cpython-311.pyc
│  │     │     ├─ sortedset.cpython-311.pyc
│  │     │     └─ __init__.cpython-311.pyc
│  │     ├─ sortedcontainers-2.4.0.dist-info
│  │     │  ├─ INSTALLER
│  │     │  ├─ LICENSE
│  │     │  ├─ METADATA
│  │     │  ├─ RECORD
│  │     │  ├─ top_level.txt
│  │     │  └─ WHEEL
│  │     ├─ soupsieve
│  │     │  ├─ css_match.py
│  │     │  ├─ css_parser.py
│  │     │  ├─ css_types.py
│  │     │  ├─ pretty.py
│  │     │  ├─ py.typed
│  │     │  ├─ util.py
│  │     │  ├─ __init__.py
│  │     │  ├─ __meta__.py
│  │     │  └─ __pycache__
│  │     │     ├─ css_match.cpython-311.pyc
│  │     │     ├─ css_parser.cpython-311.pyc
│  │     │     ├─ css_types.cpython-311.pyc
│  │     │     ├─ pretty.cpython-311.pyc
│  │     │     ├─ util.cpython-311.pyc
│  │     │     ├─ __init__.cpython-311.pyc
│  │     │     └─ __meta__.cpython-311.pyc
│  │     ├─ soupsieve-2.7.dist-info
│  │     │  ├─ INSTALLER
│  │     │  ├─ licenses
│  │     │  │  └─ LICENSE.md
│  │     │  ├─ METADATA
│  │     │  ├─ RECORD
│  │     │  └─ WHEEL
│  │     ├─ sqlalchemy
│  │     │  ├─ connectors
│  │     │  │  ├─ aioodbc.py
│  │     │  │  ├─ asyncio.py
│  │     │  │  ├─ pyodbc.py
│  │     │  │  ├─ __init__.py
│  │     │  │  └─ __pycache__
│  │     │  │     ├─ aioodbc.cpython-311.pyc
│  │     │  │     ├─ asyncio.cpython-311.pyc
│  │     │  │     ├─ pyodbc.cpython-311.pyc
│  │     │  │     └─ __init__.cpython-311.pyc
│  │     │  ├─ cyextension
│  │     │  │  ├─ collections.cp311-win_amd64.pyd
│  │     │  │  ├─ collections.pyx
│  │     │  │  ├─ immutabledict.cp311-win_amd64.pyd
│  │     │  │  ├─ immutabledict.pxd
│  │     │  │  ├─ immutabledict.pyx
│  │     │  │  ├─ processors.cp311-win_amd64.pyd
│  │     │  │  ├─ processors.pyx
│  │     │  │  ├─ resultproxy.cp311-win_amd64.pyd
│  │     │  │  ├─ resultproxy.pyx
│  │     │  │  ├─ util.cp311-win_amd64.pyd
│  │     │  │  ├─ util.pyx
│  │     │  │  ├─ __init__.py
│  │     │  │  └─ __pycache__
│  │     │  │     └─ __init__.cpython-311.pyc
│  │     │  ├─ dialects
│  │     │  │  ├─ mssql
│  │     │  │  │  ├─ aioodbc.py
│  │     │  │  │  ├─ base.py
│  │     │  │  │  ├─ information_schema.py
│  │     │  │  │  ├─ json.py
│  │     │  │  │  ├─ provision.py
│  │     │  │  │  ├─ pymssql.py
│  │     │  │  │  ├─ pyodbc.py
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ aioodbc.cpython-311.pyc
│  │     │  │  │     ├─ base.cpython-311.pyc
│  │     │  │  │     ├─ information_schema.cpython-311.pyc
│  │     │  │  │     ├─ json.cpython-311.pyc
│  │     │  │  │     ├─ provision.cpython-311.pyc
│  │     │  │  │     ├─ pymssql.cpython-311.pyc
│  │     │  │  │     ├─ pyodbc.cpython-311.pyc
│  │     │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  ├─ mysql
│  │     │  │  │  ├─ aiomysql.py
│  │     │  │  │  ├─ asyncmy.py
│  │     │  │  │  ├─ base.py
│  │     │  │  │  ├─ cymysql.py
│  │     │  │  │  ├─ dml.py
│  │     │  │  │  ├─ enumerated.py
│  │     │  │  │  ├─ expression.py
│  │     │  │  │  ├─ json.py
│  │     │  │  │  ├─ mariadb.py
│  │     │  │  │  ├─ mariadbconnector.py
│  │     │  │  │  ├─ mysqlconnector.py
│  │     │  │  │  ├─ mysqldb.py
│  │     │  │  │  ├─ provision.py
│  │     │  │  │  ├─ pymysql.py
│  │     │  │  │  ├─ pyodbc.py
│  │     │  │  │  ├─ reflection.py
│  │     │  │  │  ├─ reserved_words.py
│  │     │  │  │  ├─ types.py
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ aiomysql.cpython-311.pyc
│  │     │  │  │     ├─ asyncmy.cpython-311.pyc
│  │     │  │  │     ├─ base.cpython-311.pyc
│  │     │  │  │     ├─ cymysql.cpython-311.pyc
│  │     │  │  │     ├─ dml.cpython-311.pyc
│  │     │  │  │     ├─ enumerated.cpython-311.pyc
│  │     │  │  │     ├─ expression.cpython-311.pyc
│  │     │  │  │     ├─ json.cpython-311.pyc
│  │     │  │  │     ├─ mariadb.cpython-311.pyc
│  │     │  │  │     ├─ mariadbconnector.cpython-311.pyc
│  │     │  │  │     ├─ mysqlconnector.cpython-311.pyc
│  │     │  │  │     ├─ mysqldb.cpython-311.pyc
│  │     │  │  │     ├─ provision.cpython-311.pyc
│  │     │  │  │     ├─ pymysql.cpython-311.pyc
│  │     │  │  │     ├─ pyodbc.cpython-311.pyc
│  │     │  │  │     ├─ reflection.cpython-311.pyc
│  │     │  │  │     ├─ reserved_words.cpython-311.pyc
│  │     │  │  │     ├─ types.cpython-311.pyc
│  │     │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  ├─ oracle
│  │     │  │  │  ├─ base.py
│  │     │  │  │  ├─ cx_oracle.py
│  │     │  │  │  ├─ dictionary.py
│  │     │  │  │  ├─ oracledb.py
│  │     │  │  │  ├─ provision.py
│  │     │  │  │  ├─ types.py
│  │     │  │  │  ├─ vector.py
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ base.cpython-311.pyc
│  │     │  │  │     ├─ cx_oracle.cpython-311.pyc
│  │     │  │  │     ├─ dictionary.cpython-311.pyc
│  │     │  │  │     ├─ oracledb.cpython-311.pyc
│  │     │  │  │     ├─ provision.cpython-311.pyc
│  │     │  │  │     ├─ types.cpython-311.pyc
│  │     │  │  │     ├─ vector.cpython-311.pyc
│  │     │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  ├─ postgresql
│  │     │  │  │  ├─ array.py
│  │     │  │  │  ├─ asyncpg.py
│  │     │  │  │  ├─ base.py
│  │     │  │  │  ├─ dml.py
│  │     │  │  │  ├─ ext.py
│  │     │  │  │  ├─ hstore.py
│  │     │  │  │  ├─ json.py
│  │     │  │  │  ├─ named_types.py
│  │     │  │  │  ├─ operators.py
│  │     │  │  │  ├─ pg8000.py
│  │     │  │  │  ├─ pg_catalog.py
│  │     │  │  │  ├─ provision.py
│  │     │  │  │  ├─ psycopg.py
│  │     │  │  │  ├─ psycopg2.py
│  │     │  │  │  ├─ psycopg2cffi.py
│  │     │  │  │  ├─ ranges.py
│  │     │  │  │  ├─ types.py
│  │     │  │  │  ├─ _psycopg_common.py
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ array.cpython-311.pyc
│  │     │  │  │     ├─ asyncpg.cpython-311.pyc
│  │     │  │  │     ├─ base.cpython-311.pyc
│  │     │  │  │     ├─ dml.cpython-311.pyc
│  │     │  │  │     ├─ ext.cpython-311.pyc
│  │     │  │  │     ├─ hstore.cpython-311.pyc
│  │     │  │  │     ├─ json.cpython-311.pyc
│  │     │  │  │     ├─ named_types.cpython-311.pyc
│  │     │  │  │     ├─ operators.cpython-311.pyc
│  │     │  │  │     ├─ pg8000.cpython-311.pyc
│  │     │  │  │     ├─ pg_catalog.cpython-311.pyc
│  │     │  │  │     ├─ provision.cpython-311.pyc
│  │     │  │  │     ├─ psycopg.cpython-311.pyc
│  │     │  │  │     ├─ psycopg2.cpython-311.pyc
│  │     │  │  │     ├─ psycopg2cffi.cpython-311.pyc
│  │     │  │  │     ├─ ranges.cpython-311.pyc
│  │     │  │  │     ├─ types.cpython-311.pyc
│  │     │  │  │     ├─ _psycopg_common.cpython-311.pyc
│  │     │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  ├─ sqlite
│  │     │  │  │  ├─ aiosqlite.py
│  │     │  │  │  ├─ base.py
│  │     │  │  │  ├─ dml.py
│  │     │  │  │  ├─ json.py
│  │     │  │  │  ├─ provision.py
│  │     │  │  │  ├─ pysqlcipher.py
│  │     │  │  │  ├─ pysqlite.py
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ aiosqlite.cpython-311.pyc
│  │     │  │  │     ├─ base.cpython-311.pyc
│  │     │  │  │     ├─ dml.cpython-311.pyc
│  │     │  │  │     ├─ json.cpython-311.pyc
│  │     │  │  │     ├─ provision.cpython-311.pyc
│  │     │  │  │     ├─ pysqlcipher.cpython-311.pyc
│  │     │  │  │     ├─ pysqlite.cpython-311.pyc
│  │     │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  ├─ type_migration_guidelines.txt
│  │     │  │  ├─ _typing.py
│  │     │  │  ├─ __init__.py
│  │     │  │  └─ __pycache__
│  │     │  │     ├─ _typing.cpython-311.pyc
│  │     │  │     └─ __init__.cpython-311.pyc
│  │     │  ├─ engine
│  │     │  │  ├─ base.py
│  │     │  │  ├─ characteristics.py
│  │     │  │  ├─ create.py
│  │     │  │  ├─ cursor.py
│  │     │  │  ├─ default.py
│  │     │  │  ├─ events.py
│  │     │  │  ├─ interfaces.py
│  │     │  │  ├─ mock.py
│  │     │  │  ├─ processors.py
│  │     │  │  ├─ reflection.py
│  │     │  │  ├─ result.py
│  │     │  │  ├─ row.py
│  │     │  │  ├─ strategies.py
│  │     │  │  ├─ url.py
│  │     │  │  ├─ util.py
│  │     │  │  ├─ _py_processors.py
│  │     │  │  ├─ _py_row.py
│  │     │  │  ├─ _py_util.py
│  │     │  │  ├─ __init__.py
│  │     │  │  └─ __pycache__
│  │     │  │     ├─ base.cpython-311.pyc
│  │     │  │     ├─ characteristics.cpython-311.pyc
│  │     │  │     ├─ create.cpython-311.pyc
│  │     │  │     ├─ cursor.cpython-311.pyc
│  │     │  │     ├─ default.cpython-311.pyc
│  │     │  │     ├─ events.cpython-311.pyc
│  │     │  │     ├─ interfaces.cpython-311.pyc
│  │     │  │     ├─ mock.cpython-311.pyc
│  │     │  │     ├─ processors.cpython-311.pyc
│  │     │  │     ├─ reflection.cpython-311.pyc
│  │     │  │     ├─ result.cpython-311.pyc
│  │     │  │     ├─ row.cpython-311.pyc
│  │     │  │     ├─ strategies.cpython-311.pyc
│  │     │  │     ├─ url.cpython-311.pyc
│  │     │  │     ├─ util.cpython-311.pyc
│  │     │  │     ├─ _py_processors.cpython-311.pyc
│  │     │  │     ├─ _py_row.cpython-311.pyc
│  │     │  │     ├─ _py_util.cpython-311.pyc
│  │     │  │     └─ __init__.cpython-311.pyc
│  │     │  ├─ event
│  │     │  │  ├─ api.py
│  │     │  │  ├─ attr.py
│  │     │  │  ├─ base.py
│  │     │  │  ├─ legacy.py
│  │     │  │  ├─ registry.py
│  │     │  │  ├─ __init__.py
│  │     │  │  └─ __pycache__
│  │     │  │     ├─ api.cpython-311.pyc
│  │     │  │     ├─ attr.cpython-311.pyc
│  │     │  │     ├─ base.cpython-311.pyc
│  │     │  │     ├─ legacy.cpython-311.pyc
│  │     │  │     ├─ registry.cpython-311.pyc
│  │     │  │     └─ __init__.cpython-311.pyc
│  │     │  ├─ events.py
│  │     │  ├─ exc.py
│  │     │  ├─ ext
│  │     │  │  ├─ associationproxy.py
│  │     │  │  ├─ asyncio
│  │     │  │  │  ├─ base.py
│  │     │  │  │  ├─ engine.py
│  │     │  │  │  ├─ exc.py
│  │     │  │  │  ├─ result.py
│  │     │  │  │  ├─ scoping.py
│  │     │  │  │  ├─ session.py
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ base.cpython-311.pyc
│  │     │  │  │     ├─ engine.cpython-311.pyc
│  │     │  │  │     ├─ exc.cpython-311.pyc
│  │     │  │  │     ├─ result.cpython-311.pyc
│  │     │  │  │     ├─ scoping.cpython-311.pyc
│  │     │  │  │     ├─ session.cpython-311.pyc
│  │     │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  ├─ automap.py
│  │     │  │  ├─ baked.py
│  │     │  │  ├─ compiler.py
│  │     │  │  ├─ declarative
│  │     │  │  │  ├─ extensions.py
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ extensions.cpython-311.pyc
│  │     │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  ├─ horizontal_shard.py
│  │     │  │  ├─ hybrid.py
│  │     │  │  ├─ indexable.py
│  │     │  │  ├─ instrumentation.py
│  │     │  │  ├─ mutable.py
│  │     │  │  ├─ mypy
│  │     │  │  │  ├─ apply.py
│  │     │  │  │  ├─ decl_class.py
│  │     │  │  │  ├─ infer.py
│  │     │  │  │  ├─ names.py
│  │     │  │  │  ├─ plugin.py
│  │     │  │  │  ├─ util.py
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ apply.cpython-311.pyc
│  │     │  │  │     ├─ decl_class.cpython-311.pyc
│  │     │  │  │     ├─ infer.cpython-311.pyc
│  │     │  │  │     ├─ names.cpython-311.pyc
│  │     │  │  │     ├─ plugin.cpython-311.pyc
│  │     │  │  │     ├─ util.cpython-311.pyc
│  │     │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  ├─ orderinglist.py
│  │     │  │  ├─ serializer.py
│  │     │  │  ├─ __init__.py
│  │     │  │  └─ __pycache__
│  │     │  │     ├─ associationproxy.cpython-311.pyc
│  │     │  │     ├─ automap.cpython-311.pyc
│  │     │  │     ├─ baked.cpython-311.pyc
│  │     │  │     ├─ compiler.cpython-311.pyc
│  │     │  │     ├─ horizontal_shard.cpython-311.pyc
│  │     │  │     ├─ hybrid.cpython-311.pyc
│  │     │  │     ├─ indexable.cpython-311.pyc
│  │     │  │     ├─ instrumentation.cpython-311.pyc
│  │     │  │     ├─ mutable.cpython-311.pyc
│  │     │  │     ├─ orderinglist.cpython-311.pyc
│  │     │  │     ├─ serializer.cpython-311.pyc
│  │     │  │     └─ __init__.cpython-311.pyc
│  │     │  ├─ future
│  │     │  │  ├─ engine.py
│  │     │  │  ├─ __init__.py
│  │     │  │  └─ __pycache__
│  │     │  │     ├─ engine.cpython-311.pyc
│  │     │  │     └─ __init__.cpython-311.pyc
│  │     │  ├─ inspection.py
│  │     │  ├─ log.py
│  │     │  ├─ orm
│  │     │  │  ├─ attributes.py
│  │     │  │  ├─ base.py
│  │     │  │  ├─ bulk_persistence.py
│  │     │  │  ├─ clsregistry.py
│  │     │  │  ├─ collections.py
│  │     │  │  ├─ context.py
│  │     │  │  ├─ decl_api.py
│  │     │  │  ├─ decl_base.py
│  │     │  │  ├─ dependency.py
│  │     │  │  ├─ descriptor_props.py
│  │     │  │  ├─ dynamic.py
│  │     │  │  ├─ evaluator.py
│  │     │  │  ├─ events.py
│  │     │  │  ├─ exc.py
│  │     │  │  ├─ identity.py
│  │     │  │  ├─ instrumentation.py
│  │     │  │  ├─ interfaces.py
│  │     │  │  ├─ loading.py
│  │     │  │  ├─ mapped_collection.py
│  │     │  │  ├─ mapper.py
│  │     │  │  ├─ path_registry.py
│  │     │  │  ├─ persistence.py
│  │     │  │  ├─ properties.py
│  │     │  │  ├─ query.py
│  │     │  │  ├─ relationships.py
│  │     │  │  ├─ scoping.py
│  │     │  │  ├─ session.py
│  │     │  │  ├─ state.py
│  │     │  │  ├─ state_changes.py
│  │     │  │  ├─ strategies.py
│  │     │  │  ├─ strategy_options.py
│  │     │  │  ├─ sync.py
│  │     │  │  ├─ unitofwork.py
│  │     │  │  ├─ util.py
│  │     │  │  ├─ writeonly.py
│  │     │  │  ├─ _orm_constructors.py
│  │     │  │  ├─ _typing.py
│  │     │  │  ├─ __init__.py
│  │     │  │  └─ __pycache__
│  │     │  │     ├─ attributes.cpython-311.pyc
│  │     │  │     ├─ base.cpython-311.pyc
│  │     │  │     ├─ bulk_persistence.cpython-311.pyc
│  │     │  │     ├─ clsregistry.cpython-311.pyc
│  │     │  │     ├─ collections.cpython-311.pyc
│  │     │  │     ├─ context.cpython-311.pyc
│  │     │  │     ├─ decl_api.cpython-311.pyc
│  │     │  │     ├─ decl_base.cpython-311.pyc
│  │     │  │     ├─ dependency.cpython-311.pyc
│  │     │  │     ├─ descriptor_props.cpython-311.pyc
│  │     │  │     ├─ dynamic.cpython-311.pyc
│  │     │  │     ├─ evaluator.cpython-311.pyc
│  │     │  │     ├─ events.cpython-311.pyc
│  │     │  │     ├─ exc.cpython-311.pyc
│  │     │  │     ├─ identity.cpython-311.pyc
│  │     │  │     ├─ instrumentation.cpython-311.pyc
│  │     │  │     ├─ interfaces.cpython-311.pyc
│  │     │  │     ├─ loading.cpython-311.pyc
│  │     │  │     ├─ mapped_collection.cpython-311.pyc
│  │     │  │     ├─ mapper.cpython-311.pyc
│  │     │  │     ├─ path_registry.cpython-311.pyc
│  │     │  │     ├─ persistence.cpython-311.pyc
│  │     │  │     ├─ properties.cpython-311.pyc
│  │     │  │     ├─ query.cpython-311.pyc
│  │     │  │     ├─ relationships.cpython-311.pyc
│  │     │  │     ├─ scoping.cpython-311.pyc
│  │     │  │     ├─ session.cpython-311.pyc
│  │     │  │     ├─ state.cpython-311.pyc
│  │     │  │     ├─ state_changes.cpython-311.pyc
│  │     │  │     ├─ strategies.cpython-311.pyc
│  │     │  │     ├─ strategy_options.cpython-311.pyc
│  │     │  │     ├─ sync.cpython-311.pyc
│  │     │  │     ├─ unitofwork.cpython-311.pyc
│  │     │  │     ├─ util.cpython-311.pyc
│  │     │  │     ├─ writeonly.cpython-311.pyc
│  │     │  │     ├─ _orm_constructors.cpython-311.pyc
│  │     │  │     ├─ _typing.cpython-311.pyc
│  │     │  │     └─ __init__.cpython-311.pyc
│  │     │  ├─ pool
│  │     │  │  ├─ base.py
│  │     │  │  ├─ events.py
│  │     │  │  ├─ impl.py
│  │     │  │  ├─ __init__.py
│  │     │  │  └─ __pycache__
│  │     │  │     ├─ base.cpython-311.pyc
│  │     │  │     ├─ events.cpython-311.pyc
│  │     │  │     ├─ impl.cpython-311.pyc
│  │     │  │     └─ __init__.cpython-311.pyc
│  │     │  ├─ py.typed
│  │     │  ├─ schema.py
│  │     │  ├─ sql
│  │     │  │  ├─ annotation.py
│  │     │  │  ├─ base.py
│  │     │  │  ├─ cache_key.py
│  │     │  │  ├─ coercions.py
│  │     │  │  ├─ compiler.py
│  │     │  │  ├─ crud.py
│  │     │  │  ├─ ddl.py
│  │     │  │  ├─ default_comparator.py
│  │     │  │  ├─ dml.py
│  │     │  │  ├─ elements.py
│  │     │  │  ├─ events.py
│  │     │  │  ├─ expression.py
│  │     │  │  ├─ functions.py
│  │     │  │  ├─ lambdas.py
│  │     │  │  ├─ naming.py
│  │     │  │  ├─ operators.py
│  │     │  │  ├─ roles.py
│  │     │  │  ├─ schema.py
│  │     │  │  ├─ selectable.py
│  │     │  │  ├─ sqltypes.py
│  │     │  │  ├─ traversals.py
│  │     │  │  ├─ type_api.py
│  │     │  │  ├─ util.py
│  │     │  │  ├─ visitors.py
│  │     │  │  ├─ _dml_constructors.py
│  │     │  │  ├─ _elements_constructors.py
│  │     │  │  ├─ _orm_types.py
│  │     │  │  ├─ _py_util.py
│  │     │  │  ├─ _selectable_constructors.py
│  │     │  │  ├─ _typing.py
│  │     │  │  ├─ __init__.py
│  │     │  │  └─ __pycache__
│  │     │  │     ├─ annotation.cpython-311.pyc
│  │     │  │     ├─ base.cpython-311.pyc
│  │     │  │     ├─ cache_key.cpython-311.pyc
│  │     │  │     ├─ coercions.cpython-311.pyc
│  │     │  │     ├─ compiler.cpython-311.pyc
│  │     │  │     ├─ crud.cpython-311.pyc
│  │     │  │     ├─ ddl.cpython-311.pyc
│  │     │  │     ├─ default_comparator.cpython-311.pyc
│  │     │  │     ├─ dml.cpython-311.pyc
│  │     │  │     ├─ elements.cpython-311.pyc
│  │     │  │     ├─ events.cpython-311.pyc
│  │     │  │     ├─ expression.cpython-311.pyc
│  │     │  │     ├─ functions.cpython-311.pyc
│  │     │  │     ├─ lambdas.cpython-311.pyc
│  │     │  │     ├─ naming.cpython-311.pyc
│  │     │  │     ├─ operators.cpython-311.pyc
│  │     │  │     ├─ roles.cpython-311.pyc
│  │     │  │     ├─ schema.cpython-311.pyc
│  │     │  │     ├─ selectable.cpython-311.pyc
│  │     │  │     ├─ sqltypes.cpython-311.pyc
│  │     │  │     ├─ traversals.cpython-311.pyc
│  │     │  │     ├─ type_api.cpython-311.pyc
│  │     │  │     ├─ util.cpython-311.pyc
│  │     │  │     ├─ visitors.cpython-311.pyc
│  │     │  │     ├─ _dml_constructors.cpython-311.pyc
│  │     │  │     ├─ _elements_constructors.cpython-311.pyc
│  │     │  │     ├─ _orm_types.cpython-311.pyc
│  │     │  │     ├─ _py_util.cpython-311.pyc
│  │     │  │     ├─ _selectable_constructors.cpython-311.pyc
│  │     │  │     ├─ _typing.cpython-311.pyc
│  │     │  │     └─ __init__.cpython-311.pyc
│  │     │  ├─ testing
│  │     │  │  ├─ assertions.py
│  │     │  │  ├─ assertsql.py
│  │     │  │  ├─ asyncio.py
│  │     │  │  ├─ config.py
│  │     │  │  ├─ engines.py
│  │     │  │  ├─ entities.py
│  │     │  │  ├─ exclusions.py
│  │     │  │  ├─ fixtures
│  │     │  │  │  ├─ base.py
│  │     │  │  │  ├─ mypy.py
│  │     │  │  │  ├─ orm.py
│  │     │  │  │  ├─ sql.py
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ base.cpython-311.pyc
│  │     │  │  │     ├─ mypy.cpython-311.pyc
│  │     │  │  │     ├─ orm.cpython-311.pyc
│  │     │  │  │     ├─ sql.cpython-311.pyc
│  │     │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  ├─ pickleable.py
│  │     │  │  ├─ plugin
│  │     │  │  │  ├─ bootstrap.py
│  │     │  │  │  ├─ plugin_base.py
│  │     │  │  │  ├─ pytestplugin.py
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ bootstrap.cpython-311.pyc
│  │     │  │  │     ├─ plugin_base.cpython-311.pyc
│  │     │  │  │     ├─ pytestplugin.cpython-311.pyc
│  │     │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  ├─ profiling.py
│  │     │  │  ├─ provision.py
│  │     │  │  ├─ requirements.py
│  │     │  │  ├─ schema.py
│  │     │  │  ├─ suite
│  │     │  │  │  ├─ test_cte.py
│  │     │  │  │  ├─ test_ddl.py
│  │     │  │  │  ├─ test_deprecations.py
│  │     │  │  │  ├─ test_dialect.py
│  │     │  │  │  ├─ test_insert.py
│  │     │  │  │  ├─ test_reflection.py
│  │     │  │  │  ├─ test_results.py
│  │     │  │  │  ├─ test_rowcount.py
│  │     │  │  │  ├─ test_select.py
│  │     │  │  │  ├─ test_sequence.py
│  │     │  │  │  ├─ test_types.py
│  │     │  │  │  ├─ test_unicode_ddl.py
│  │     │  │  │  ├─ test_update_delete.py
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ test_cte.cpython-311.pyc
│  │     │  │  │     ├─ test_ddl.cpython-311.pyc
│  │     │  │  │     ├─ test_deprecations.cpython-311.pyc
│  │     │  │  │     ├─ test_dialect.cpython-311.pyc
│  │     │  │  │     ├─ test_insert.cpython-311.pyc
│  │     │  │  │     ├─ test_reflection.cpython-311.pyc
│  │     │  │  │     ├─ test_results.cpython-311.pyc
│  │     │  │  │     ├─ test_rowcount.cpython-311.pyc
│  │     │  │  │     ├─ test_select.cpython-311.pyc
│  │     │  │  │     ├─ test_sequence.cpython-311.pyc
│  │     │  │  │     ├─ test_types.cpython-311.pyc
│  │     │  │  │     ├─ test_unicode_ddl.cpython-311.pyc
│  │     │  │  │     ├─ test_update_delete.cpython-311.pyc
│  │     │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  ├─ util.py
│  │     │  │  ├─ warnings.py
│  │     │  │  ├─ __init__.py
│  │     │  │  └─ __pycache__
│  │     │  │     ├─ assertions.cpython-311.pyc
│  │     │  │     ├─ assertsql.cpython-311.pyc
│  │     │  │     ├─ asyncio.cpython-311.pyc
│  │     │  │     ├─ config.cpython-311.pyc
│  │     │  │     ├─ engines.cpython-311.pyc
│  │     │  │     ├─ entities.cpython-311.pyc
│  │     │  │     ├─ exclusions.cpython-311.pyc
│  │     │  │     ├─ pickleable.cpython-311.pyc
│  │     │  │     ├─ profiling.cpython-311.pyc
│  │     │  │     ├─ provision.cpython-311.pyc
│  │     │  │     ├─ requirements.cpython-311.pyc
│  │     │  │     ├─ schema.cpython-311.pyc
│  │     │  │     ├─ util.cpython-311.pyc
│  │     │  │     ├─ warnings.cpython-311.pyc
│  │     │  │     └─ __init__.cpython-311.pyc
│  │     │  ├─ types.py
│  │     │  ├─ util
│  │     │  │  ├─ compat.py
│  │     │  │  ├─ concurrency.py
│  │     │  │  ├─ deprecations.py
│  │     │  │  ├─ langhelpers.py
│  │     │  │  ├─ preloaded.py
│  │     │  │  ├─ queue.py
│  │     │  │  ├─ tool_support.py
│  │     │  │  ├─ topological.py
│  │     │  │  ├─ typing.py
│  │     │  │  ├─ _collections.py
│  │     │  │  ├─ _concurrency_py3k.py
│  │     │  │  ├─ _has_cy.py
│  │     │  │  ├─ _py_collections.py
│  │     │  │  ├─ __init__.py
│  │     │  │  └─ __pycache__
│  │     │  │     ├─ compat.cpython-311.pyc
│  │     │  │     ├─ concurrency.cpython-311.pyc
│  │     │  │     ├─ deprecations.cpython-311.pyc
│  │     │  │     ├─ langhelpers.cpython-311.pyc
│  │     │  │     ├─ preloaded.cpython-311.pyc
│  │     │  │     ├─ queue.cpython-311.pyc
│  │     │  │     ├─ tool_support.cpython-311.pyc
│  │     │  │     ├─ topological.cpython-311.pyc
│  │     │  │     ├─ typing.cpython-311.pyc
│  │     │  │     ├─ _collections.cpython-311.pyc
│  │     │  │     ├─ _concurrency_py3k.cpython-311.pyc
│  │     │  │     ├─ _has_cy.cpython-311.pyc
│  │     │  │     ├─ _py_collections.cpython-311.pyc
│  │     │  │     └─ __init__.cpython-311.pyc
│  │     │  ├─ __init__.py
│  │     │  └─ __pycache__
│  │     │     ├─ events.cpython-311.pyc
│  │     │     ├─ exc.cpython-311.pyc
│  │     │     ├─ inspection.cpython-311.pyc
│  │     │     ├─ log.cpython-311.pyc
│  │     │     ├─ schema.cpython-311.pyc
│  │     │     ├─ types.cpython-311.pyc
│  │     │     └─ __init__.cpython-311.pyc
│  │     ├─ sqlalchemy-2.0.41.dist-info
│  │     │  ├─ INSTALLER
│  │     │  ├─ licenses
│  │     │  │  └─ LICENSE
│  │     │  ├─ METADATA
│  │     │  ├─ RECORD
│  │     │  ├─ REQUESTED
│  │     │  ├─ top_level.txt
│  │     │  └─ WHEEL
│  │     ├─ trio
│  │     │  ├─ abc.py
│  │     │  ├─ from_thread.py
│  │     │  ├─ lowlevel.py
│  │     │  ├─ py.typed
│  │     │  ├─ socket.py
│  │     │  ├─ testing
│  │     │  │  ├─ _checkpoints.py
│  │     │  │  ├─ _check_streams.py
│  │     │  │  ├─ _fake_net.py
│  │     │  │  ├─ _memory_streams.py
│  │     │  │  ├─ _network.py
│  │     │  │  ├─ _raises_group.py
│  │     │  │  ├─ _sequencer.py
│  │     │  │  ├─ _trio_test.py
│  │     │  │  ├─ __init__.py
│  │     │  │  └─ __pycache__
│  │     │  │     ├─ _checkpoints.cpython-311.pyc
│  │     │  │     ├─ _check_streams.cpython-311.pyc
│  │     │  │     ├─ _fake_net.cpython-311.pyc
│  │     │  │     ├─ _memory_streams.cpython-311.pyc
│  │     │  │     ├─ _network.cpython-311.pyc
│  │     │  │     ├─ _raises_group.cpython-311.pyc
│  │     │  │     ├─ _sequencer.cpython-311.pyc
│  │     │  │     ├─ _trio_test.cpython-311.pyc
│  │     │  │     └─ __init__.cpython-311.pyc
│  │     │  ├─ to_thread.py
│  │     │  ├─ _abc.py
│  │     │  ├─ _channel.py
│  │     │  ├─ _core
│  │     │  │  ├─ _asyncgens.py
│  │     │  │  ├─ _concat_tb.py
│  │     │  │  ├─ _entry_queue.py
│  │     │  │  ├─ _exceptions.py
│  │     │  │  ├─ _generated_instrumentation.py
│  │     │  │  ├─ _generated_io_epoll.py
│  │     │  │  ├─ _generated_io_kqueue.py
│  │     │  │  ├─ _generated_io_windows.py
│  │     │  │  ├─ _generated_run.py
│  │     │  │  ├─ _instrumentation.py
│  │     │  │  ├─ _io_common.py
│  │     │  │  ├─ _io_epoll.py
│  │     │  │  ├─ _io_kqueue.py
│  │     │  │  ├─ _io_windows.py
│  │     │  │  ├─ _ki.py
│  │     │  │  ├─ _local.py
│  │     │  │  ├─ _mock_clock.py
│  │     │  │  ├─ _parking_lot.py
│  │     │  │  ├─ _run.py
│  │     │  │  ├─ _run_context.py
│  │     │  │  ├─ _tests
│  │     │  │  │  ├─ test_asyncgen.py
│  │     │  │  │  ├─ test_exceptiongroup_gc.py
│  │     │  │  │  ├─ test_guest_mode.py
│  │     │  │  │  ├─ test_instrumentation.py
│  │     │  │  │  ├─ test_io.py
│  │     │  │  │  ├─ test_ki.py
│  │     │  │  │  ├─ test_local.py
│  │     │  │  │  ├─ test_mock_clock.py
│  │     │  │  │  ├─ test_parking_lot.py
│  │     │  │  │  ├─ test_run.py
│  │     │  │  │  ├─ test_thread_cache.py
│  │     │  │  │  ├─ test_tutil.py
│  │     │  │  │  ├─ test_unbounded_queue.py
│  │     │  │  │  ├─ test_windows.py
│  │     │  │  │  ├─ tutil.py
│  │     │  │  │  ├─ type_tests
│  │     │  │  │  │  ├─ nursery_start.py
│  │     │  │  │  │  ├─ run.py
│  │     │  │  │  │  └─ __pycache__
│  │     │  │  │  │     ├─ nursery_start.cpython-311.pyc
│  │     │  │  │  │     └─ run.cpython-311.pyc
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ test_asyncgen.cpython-311.pyc
│  │     │  │  │     ├─ test_exceptiongroup_gc.cpython-311.pyc
│  │     │  │  │     ├─ test_guest_mode.cpython-311.pyc
│  │     │  │  │     ├─ test_instrumentation.cpython-311.pyc
│  │     │  │  │     ├─ test_io.cpython-311.pyc
│  │     │  │  │     ├─ test_ki.cpython-311.pyc
│  │     │  │  │     ├─ test_local.cpython-311.pyc
│  │     │  │  │     ├─ test_mock_clock.cpython-311.pyc
│  │     │  │  │     ├─ test_parking_lot.cpython-311.pyc
│  │     │  │  │     ├─ test_run.cpython-311.pyc
│  │     │  │  │     ├─ test_thread_cache.cpython-311.pyc
│  │     │  │  │     ├─ test_tutil.cpython-311.pyc
│  │     │  │  │     ├─ test_unbounded_queue.cpython-311.pyc
│  │     │  │  │     ├─ test_windows.cpython-311.pyc
│  │     │  │  │     ├─ tutil.cpython-311.pyc
│  │     │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  ├─ _thread_cache.py
│  │     │  │  ├─ _traps.py
│  │     │  │  ├─ _unbounded_queue.py
│  │     │  │  ├─ _wakeup_socketpair.py
│  │     │  │  ├─ _windows_cffi.py
│  │     │  │  ├─ __init__.py
│  │     │  │  └─ __pycache__
│  │     │  │     ├─ _asyncgens.cpython-311.pyc
│  │     │  │     ├─ _concat_tb.cpython-311.pyc
│  │     │  │     ├─ _entry_queue.cpython-311.pyc
│  │     │  │     ├─ _exceptions.cpython-311.pyc
│  │     │  │     ├─ _generated_instrumentation.cpython-311.pyc
│  │     │  │     ├─ _generated_io_epoll.cpython-311.pyc
│  │     │  │     ├─ _generated_io_kqueue.cpython-311.pyc
│  │     │  │     ├─ _generated_io_windows.cpython-311.pyc
│  │     │  │     ├─ _generated_run.cpython-311.pyc
│  │     │  │     ├─ _instrumentation.cpython-311.pyc
│  │     │  │     ├─ _io_common.cpython-311.pyc
│  │     │  │     ├─ _io_epoll.cpython-311.pyc
│  │     │  │     ├─ _io_kqueue.cpython-311.pyc
│  │     │  │     ├─ _io_windows.cpython-311.pyc
│  │     │  │     ├─ _ki.cpython-311.pyc
│  │     │  │     ├─ _local.cpython-311.pyc
│  │     │  │     ├─ _mock_clock.cpython-311.pyc
│  │     │  │     ├─ _parking_lot.cpython-311.pyc
│  │     │  │     ├─ _run.cpython-311.pyc
│  │     │  │     ├─ _run_context.cpython-311.pyc
│  │     │  │     ├─ _thread_cache.cpython-311.pyc
│  │     │  │     ├─ _traps.cpython-311.pyc
│  │     │  │     ├─ _unbounded_queue.cpython-311.pyc
│  │     │  │     ├─ _wakeup_socketpair.cpython-311.pyc
│  │     │  │     ├─ _windows_cffi.cpython-311.pyc
│  │     │  │     └─ __init__.cpython-311.pyc
│  │     │  ├─ _deprecate.py
│  │     │  ├─ _dtls.py
│  │     │  ├─ _file_io.py
│  │     │  ├─ _highlevel_generic.py
│  │     │  ├─ _highlevel_open_tcp_listeners.py
│  │     │  ├─ _highlevel_open_tcp_stream.py
│  │     │  ├─ _highlevel_open_unix_stream.py
│  │     │  ├─ _highlevel_serve_listeners.py
│  │     │  ├─ _highlevel_socket.py
│  │     │  ├─ _highlevel_ssl_helpers.py
│  │     │  ├─ _path.py
│  │     │  ├─ _repl.py
│  │     │  ├─ _signals.py
│  │     │  ├─ _socket.py
│  │     │  ├─ _ssl.py
│  │     │  ├─ _subprocess.py
│  │     │  ├─ _subprocess_platform
│  │     │  │  ├─ kqueue.py
│  │     │  │  ├─ waitid.py
│  │     │  │  ├─ windows.py
│  │     │  │  ├─ __init__.py
│  │     │  │  └─ __pycache__
│  │     │  │     ├─ kqueue.cpython-311.pyc
│  │     │  │     ├─ waitid.cpython-311.pyc
│  │     │  │     ├─ windows.cpython-311.pyc
│  │     │  │     └─ __init__.cpython-311.pyc
│  │     │  ├─ _sync.py
│  │     │  ├─ _tests
│  │     │  │  ├─ astrill-codesigning-cert.cer
│  │     │  │  ├─ check_type_completeness.py
│  │     │  │  ├─ module_with_deprecations.py
│  │     │  │  ├─ pytest_plugin.py
│  │     │  │  ├─ test_abc.py
│  │     │  │  ├─ test_channel.py
│  │     │  │  ├─ test_contextvars.py
│  │     │  │  ├─ test_deprecate.py
│  │     │  │  ├─ test_deprecate_strict_exception_groups_false.py
│  │     │  │  ├─ test_dtls.py
│  │     │  │  ├─ test_exports.py
│  │     │  │  ├─ test_fakenet.py
│  │     │  │  ├─ test_file_io.py
│  │     │  │  ├─ test_highlevel_generic.py
│  │     │  │  ├─ test_highlevel_open_tcp_listeners.py
│  │     │  │  ├─ test_highlevel_open_tcp_stream.py
│  │     │  │  ├─ test_highlevel_open_unix_stream.py
│  │     │  │  ├─ test_highlevel_serve_listeners.py
│  │     │  │  ├─ test_highlevel_socket.py
│  │     │  │  ├─ test_highlevel_ssl_helpers.py
│  │     │  │  ├─ test_path.py
│  │     │  │  ├─ test_repl.py
│  │     │  │  ├─ test_scheduler_determinism.py
│  │     │  │  ├─ test_signals.py
│  │     │  │  ├─ test_socket.py
│  │     │  │  ├─ test_ssl.py
│  │     │  │  ├─ test_subprocess.py
│  │     │  │  ├─ test_sync.py
│  │     │  │  ├─ test_testing.py
│  │     │  │  ├─ test_testing_raisesgroup.py
│  │     │  │  ├─ test_threads.py
│  │     │  │  ├─ test_timeouts.py
│  │     │  │  ├─ test_tracing.py
│  │     │  │  ├─ test_trio.py
│  │     │  │  ├─ test_unix_pipes.py
│  │     │  │  ├─ test_util.py
│  │     │  │  ├─ test_wait_for_object.py
│  │     │  │  ├─ test_windows_pipes.py
│  │     │  │  ├─ tools
│  │     │  │  │  ├─ test_gen_exports.py
│  │     │  │  │  ├─ test_mypy_annotate.py
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ test_gen_exports.cpython-311.pyc
│  │     │  │  │     ├─ test_mypy_annotate.cpython-311.pyc
│  │     │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  ├─ type_tests
│  │     │  │  │  ├─ check_wraps.py
│  │     │  │  │  ├─ open_memory_channel.py
│  │     │  │  │  ├─ path.py
│  │     │  │  │  ├─ raisesgroup.py
│  │     │  │  │  ├─ subprocesses.py
│  │     │  │  │  ├─ task_status.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ check_wraps.cpython-311.pyc
│  │     │  │  │     ├─ open_memory_channel.cpython-311.pyc
│  │     │  │  │     ├─ path.cpython-311.pyc
│  │     │  │  │     ├─ raisesgroup.cpython-311.pyc
│  │     │  │  │     ├─ subprocesses.cpython-311.pyc
│  │     │  │  │     └─ task_status.cpython-311.pyc
│  │     │  │  ├─ __init__.py
│  │     │  │  └─ __pycache__
│  │     │  │     ├─ check_type_completeness.cpython-311.pyc
│  │     │  │     ├─ module_with_deprecations.cpython-311.pyc
│  │     │  │     ├─ pytest_plugin.cpython-311.pyc
│  │     │  │     ├─ test_abc.cpython-311.pyc
│  │     │  │     ├─ test_channel.cpython-311.pyc
│  │     │  │     ├─ test_contextvars.cpython-311.pyc
│  │     │  │     ├─ test_deprecate.cpython-311.pyc
│  │     │  │     ├─ test_deprecate_strict_exception_groups_false.cpython-311.pyc
│  │     │  │     ├─ test_dtls.cpython-311.pyc
│  │     │  │     ├─ test_exports.cpython-311.pyc
│  │     │  │     ├─ test_fakenet.cpython-311.pyc
│  │     │  │     ├─ test_file_io.cpython-311.pyc
│  │     │  │     ├─ test_highlevel_generic.cpython-311.pyc
│  │     │  │     ├─ test_highlevel_open_tcp_listeners.cpython-311.pyc
│  │     │  │     ├─ test_highlevel_open_tcp_stream.cpython-311.pyc
│  │     │  │     ├─ test_highlevel_open_unix_stream.cpython-311.pyc
│  │     │  │     ├─ test_highlevel_serve_listeners.cpython-311.pyc
│  │     │  │     ├─ test_highlevel_socket.cpython-311.pyc
│  │     │  │     ├─ test_highlevel_ssl_helpers.cpython-311.pyc
│  │     │  │     ├─ test_path.cpython-311.pyc
│  │     │  │     ├─ test_repl.cpython-311.pyc
│  │     │  │     ├─ test_scheduler_determinism.cpython-311.pyc
│  │     │  │     ├─ test_signals.cpython-311.pyc
│  │     │  │     ├─ test_socket.cpython-311.pyc
│  │     │  │     ├─ test_ssl.cpython-311.pyc
│  │     │  │     ├─ test_subprocess.cpython-311.pyc
│  │     │  │     ├─ test_sync.cpython-311.pyc
│  │     │  │     ├─ test_testing.cpython-311.pyc
│  │     │  │     ├─ test_testing_raisesgroup.cpython-311.pyc
│  │     │  │     ├─ test_threads.cpython-311.pyc
│  │     │  │     ├─ test_timeouts.cpython-311.pyc
│  │     │  │     ├─ test_tracing.cpython-311.pyc
│  │     │  │     ├─ test_trio.cpython-311.pyc
│  │     │  │     ├─ test_unix_pipes.cpython-311.pyc
│  │     │  │     ├─ test_util.cpython-311.pyc
│  │     │  │     ├─ test_wait_for_object.cpython-311.pyc
│  │     │  │     ├─ test_windows_pipes.cpython-311.pyc
│  │     │  │     └─ __init__.cpython-311.pyc
│  │     │  ├─ _threads.py
│  │     │  ├─ _timeouts.py
│  │     │  ├─ _tools
│  │     │  │  ├─ gen_exports.py
│  │     │  │  ├─ mypy_annotate.py
│  │     │  │  ├─ __init__.py
│  │     │  │  └─ __pycache__
│  │     │  │     ├─ gen_exports.cpython-311.pyc
│  │     │  │     ├─ mypy_annotate.cpython-311.pyc
│  │     │  │     └─ __init__.cpython-311.pyc
│  │     │  ├─ _unix_pipes.py
│  │     │  ├─ _util.py
│  │     │  ├─ _version.py
│  │     │  ├─ _wait_for_object.py
│  │     │  ├─ _windows_pipes.py
│  │     │  ├─ __init__.py
│  │     │  ├─ __main__.py
│  │     │  └─ __pycache__
│  │     │     ├─ abc.cpython-311.pyc
│  │     │     ├─ from_thread.cpython-311.pyc
│  │     │     ├─ lowlevel.cpython-311.pyc
│  │     │     ├─ socket.cpython-311.pyc
│  │     │     ├─ to_thread.cpython-311.pyc
│  │     │     ├─ _abc.cpython-311.pyc
│  │     │     ├─ _channel.cpython-311.pyc
│  │     │     ├─ _deprecate.cpython-311.pyc
│  │     │     ├─ _dtls.cpython-311.pyc
│  │     │     ├─ _file_io.cpython-311.pyc
│  │     │     ├─ _highlevel_generic.cpython-311.pyc
│  │     │     ├─ _highlevel_open_tcp_listeners.cpython-311.pyc
│  │     │     ├─ _highlevel_open_tcp_stream.cpython-311.pyc
│  │     │     ├─ _highlevel_open_unix_stream.cpython-311.pyc
│  │     │     ├─ _highlevel_serve_listeners.cpython-311.pyc
│  │     │     ├─ _highlevel_socket.cpython-311.pyc
│  │     │     ├─ _highlevel_ssl_helpers.cpython-311.pyc
│  │     │     ├─ _path.cpython-311.pyc
│  │     │     ├─ _repl.cpython-311.pyc
│  │     │     ├─ _signals.cpython-311.pyc
│  │     │     ├─ _socket.cpython-311.pyc
│  │     │     ├─ _ssl.cpython-311.pyc
│  │     │     ├─ _subprocess.cpython-311.pyc
│  │     │     ├─ _sync.cpython-311.pyc
│  │     │     ├─ _threads.cpython-311.pyc
│  │     │     ├─ _timeouts.cpython-311.pyc
│  │     │     ├─ _unix_pipes.cpython-311.pyc
│  │     │     ├─ _util.cpython-311.pyc
│  │     │     ├─ _version.cpython-311.pyc
│  │     │     ├─ _wait_for_object.cpython-311.pyc
│  │     │     ├─ _windows_pipes.cpython-311.pyc
│  │     │     ├─ __init__.cpython-311.pyc
│  │     │     └─ __main__.cpython-311.pyc
│  │     ├─ trio-0.30.0.dist-info
│  │     │  ├─ entry_points.txt
│  │     │  ├─ INSTALLER
│  │     │  ├─ licenses
│  │     │  │  ├─ LICENSE
│  │     │  │  ├─ LICENSE.APACHE2
│  │     │  │  └─ LICENSE.MIT
│  │     │  ├─ METADATA
│  │     │  ├─ RECORD
│  │     │  ├─ top_level.txt
│  │     │  └─ WHEEL
│  │     ├─ trio_websocket
│  │     │  ├─ py.typed
│  │     │  ├─ _impl.py
│  │     │  ├─ _version.py
│  │     │  ├─ __init__.py
│  │     │  └─ __pycache__
│  │     │     ├─ _impl.cpython-311.pyc
│  │     │     ├─ _version.cpython-311.pyc
│  │     │     └─ __init__.cpython-311.pyc
│  │     ├─ trio_websocket-0.12.2.dist-info
│  │     │  ├─ INSTALLER
│  │     │  ├─ LICENSE
│  │     │  ├─ METADATA
│  │     │  ├─ RECORD
│  │     │  ├─ top_level.txt
│  │     │  └─ WHEEL
│  │     ├─ typing_extensions-4.14.1.dist-info
│  │     │  ├─ INSTALLER
│  │     │  ├─ licenses
│  │     │  │  └─ LICENSE
│  │     │  ├─ METADATA
│  │     │  ├─ RECORD
│  │     │  └─ WHEEL
│  │     ├─ typing_extensions.py
│  │     ├─ urllib3
│  │     │  ├─ connection.py
│  │     │  ├─ connectionpool.py
│  │     │  ├─ contrib
│  │     │  │  ├─ emscripten
│  │     │  │  │  ├─ connection.py
│  │     │  │  │  ├─ emscripten_fetch_worker.js
│  │     │  │  │  ├─ fetch.py
│  │     │  │  │  ├─ request.py
│  │     │  │  │  ├─ response.py
│  │     │  │  │  ├─ __init__.py
│  │     │  │  │  └─ __pycache__
│  │     │  │  │     ├─ connection.cpython-311.pyc
│  │     │  │  │     ├─ fetch.cpython-311.pyc
│  │     │  │  │     ├─ request.cpython-311.pyc
│  │     │  │  │     ├─ response.cpython-311.pyc
│  │     │  │  │     └─ __init__.cpython-311.pyc
│  │     │  │  ├─ pyopenssl.py
│  │     │  │  ├─ socks.py
│  │     │  │  ├─ __init__.py
│  │     │  │  └─ __pycache__
│  │     │  │     ├─ pyopenssl.cpython-311.pyc
│  │     │  │     ├─ socks.cpython-311.pyc
│  │     │  │     └─ __init__.cpython-311.pyc
│  │     │  ├─ exceptions.py
│  │     │  ├─ fields.py
│  │     │  ├─ filepost.py
│  │     │  ├─ http2
│  │     │  │  ├─ connection.py
│  │     │  │  ├─ probe.py
│  │     │  │  ├─ __init__.py
│  │     │  │  └─ __pycache__
│  │     │  │     ├─ connection.cpython-311.pyc
│  │     │  │     ├─ probe.cpython-311.pyc
│  │     │  │     └─ __init__.cpython-311.pyc
│  │     │  ├─ poolmanager.py
│  │     │  ├─ py.typed
│  │     │  ├─ response.py
│  │     │  ├─ util
│  │     │  │  ├─ connection.py
│  │     │  │  ├─ proxy.py
│  │     │  │  ├─ request.py
│  │     │  │  ├─ response.py
│  │     │  │  ├─ retry.py
│  │     │  │  ├─ ssltransport.py
│  │     │  │  ├─ ssl_.py
│  │     │  │  ├─ ssl_match_hostname.py
│  │     │  │  ├─ timeout.py
│  │     │  │  ├─ url.py
│  │     │  │  ├─ util.py
│  │     │  │  ├─ wait.py
│  │     │  │  ├─ __init__.py
│  │     │  │  └─ __pycache__
│  │     │  │     ├─ connection.cpython-311.pyc
│  │     │  │     ├─ proxy.cpython-311.pyc
│  │     │  │     ├─ request.cpython-311.pyc
│  │     │  │     ├─ response.cpython-311.pyc
│  │     │  │     ├─ retry.cpython-311.pyc
│  │     │  │     ├─ ssltransport.cpython-311.pyc
│  │     │  │     ├─ ssl_.cpython-311.pyc
│  │     │  │     ├─ ssl_match_hostname.cpython-311.pyc
│  │     │  │     ├─ timeout.cpython-311.pyc
│  │     │  │     ├─ url.cpython-311.pyc
│  │     │  │     ├─ util.cpython-311.pyc
│  │     │  │     ├─ wait.cpython-311.pyc
│  │     │  │     └─ __init__.cpython-311.pyc
│  │     │  ├─ _base_connection.py
│  │     │  ├─ _collections.py
│  │     │  ├─ _request_methods.py
│  │     │  ├─ _version.py
│  │     │  ├─ __init__.py
│  │     │  └─ __pycache__
│  │     │     ├─ connection.cpython-311.pyc
│  │     │     ├─ connectionpool.cpython-311.pyc
│  │     │     ├─ exceptions.cpython-311.pyc
│  │     │     ├─ fields.cpython-311.pyc
│  │     │     ├─ filepost.cpython-311.pyc
│  │     │     ├─ poolmanager.cpython-311.pyc
│  │     │     ├─ response.cpython-311.pyc
│  │     │     ├─ _base_connection.cpython-311.pyc
│  │     │     ├─ _collections.cpython-311.pyc
│  │     │     ├─ _request_methods.cpython-311.pyc
│  │     │     ├─ _version.cpython-311.pyc
│  │     │     └─ __init__.cpython-311.pyc
│  │     ├─ urllib3-2.5.0.dist-info
│  │     │  ├─ INSTALLER
│  │     │  ├─ licenses
│  │     │  │  └─ LICENSE.txt
│  │     │  ├─ METADATA
│  │     │  ├─ RECORD
│  │     │  └─ WHEEL
│  │     ├─ webdriver_manager
│  │     │  ├─ chrome.py
│  │     │  ├─ core
│  │     │  │  ├─ archive.py
│  │     │  │  ├─ config.py
│  │     │  │  ├─ constants.py
│  │     │  │  ├─ download_manager.py
│  │     │  │  ├─ driver.py
│  │     │  │  ├─ driver_cache.py
│  │     │  │  ├─ file_manager.py
│  │     │  │  ├─ http.py
│  │     │  │  ├─ logger.py
│  │     │  │  ├─ manager.py
│  │     │  │  ├─ os_manager.py
│  │     │  │  ├─ utils.py
│  │     │  │  ├─ __init__.py
│  │     │  │  └─ __pycache__
│  │     │  │     ├─ archive.cpython-311.pyc
│  │     │  │     ├─ config.cpython-311.pyc
│  │     │  │     ├─ constants.cpython-311.pyc
│  │     │  │     ├─ download_manager.cpython-311.pyc
│  │     │  │     ├─ driver.cpython-311.pyc
│  │     │  │     ├─ driver_cache.cpython-311.pyc
│  │     │  │     ├─ file_manager.cpython-311.pyc
│  │     │  │     ├─ http.cpython-311.pyc
│  │     │  │     ├─ logger.cpython-311.pyc
│  │     │  │     ├─ manager.cpython-311.pyc
│  │     │  │     ├─ os_manager.cpython-311.pyc
│  │     │  │     ├─ utils.cpython-311.pyc
│  │     │  │     └─ __init__.cpython-311.pyc
│  │     │  ├─ drivers
│  │     │  │  ├─ chrome.py
│  │     │  │  ├─ edge.py
│  │     │  │  ├─ firefox.py
│  │     │  │  ├─ ie.py
│  │     │  │  ├─ opera.py
│  │     │  │  ├─ __init__.py
│  │     │  │  └─ __pycache__
│  │     │  │     ├─ chrome.cpython-311.pyc
│  │     │  │     ├─ edge.cpython-311.pyc
│  │     │  │     ├─ firefox.cpython-311.pyc
│  │     │  │     ├─ ie.cpython-311.pyc
│  │     │  │     ├─ opera.cpython-311.pyc
│  │     │  │     └─ __init__.cpython-311.pyc
│  │     │  ├─ firefox.py
│  │     │  ├─ microsoft.py
│  │     │  ├─ opera.py
│  │     │  ├─ py.typed
│  │     │  ├─ __init__.py
│  │     │  └─ __pycache__
│  │     │     ├─ chrome.cpython-311.pyc
│  │     │     ├─ firefox.cpython-311.pyc
│  │     │     ├─ microsoft.cpython-311.pyc
│  │     │     ├─ opera.cpython-311.pyc
│  │     │     └─ __init__.cpython-311.pyc
│  │     ├─ webdriver_manager-4.0.2.dist-info
│  │     │  ├─ INSTALLER
│  │     │  ├─ LICENSE
│  │     │  ├─ METADATA
│  │     │  ├─ RECORD
│  │     │  ├─ REQUESTED
│  │     │  ├─ top_level.txt
│  │     │  └─ WHEEL
│  │     ├─ websocket
│  │     │  ├─ py.typed
│  │     │  ├─ tests
│  │     │  │  ├─ data
│  │     │  │  │  ├─ header01.txt
│  │     │  │  │  ├─ header02.txt
│  │     │  │  │  └─ header03.txt
│  │     │  │  ├─ echo-server.py
│  │     │  │  ├─ test_abnf.py
│  │     │  │  ├─ test_app.py
│  │     │  │  ├─ test_cookiejar.py
│  │     │  │  ├─ test_http.py
│  │     │  │  ├─ test_url.py
│  │     │  │  ├─ test_websocket.py
│  │     │  │  ├─ __init__.py
│  │     │  │  └─ __pycache__
│  │     │  │     ├─ echo-server.cpython-311.pyc
│  │     │  │     ├─ test_abnf.cpython-311.pyc
│  │     │  │     ├─ test_app.cpython-311.pyc
│  │     │  │     ├─ test_cookiejar.cpython-311.pyc
│  │     │  │     ├─ test_http.cpython-311.pyc
│  │     │  │     ├─ test_url.cpython-311.pyc
│  │     │  │     ├─ test_websocket.cpython-311.pyc
│  │     │  │     └─ __init__.cpython-311.pyc
│  │     │  ├─ _abnf.py
│  │     │  ├─ _app.py
│  │     │  ├─ _cookiejar.py
│  │     │  ├─ _core.py
│  │     │  ├─ _exceptions.py
│  │     │  ├─ _handshake.py
│  │     │  ├─ _http.py
│  │     │  ├─ _logging.py
│  │     │  ├─ _socket.py
│  │     │  ├─ _ssl_compat.py
│  │     │  ├─ _url.py
│  │     │  ├─ _utils.py
│  │     │  ├─ _wsdump.py
│  │     │  ├─ __init__.py
│  │     │  └─ __pycache__
│  │     │     ├─ _abnf.cpython-311.pyc
│  │     │     ├─ _app.cpython-311.pyc
│  │     │     ├─ _cookiejar.cpython-311.pyc
│  │     │     ├─ _core.cpython-311.pyc
│  │     │     ├─ _exceptions.cpython-311.pyc
│  │     │     ├─ _handshake.cpython-311.pyc
│  │     │     ├─ _http.cpython-311.pyc
│  │     │     ├─ _logging.cpython-311.pyc
│  │     │     ├─ _socket.cpython-311.pyc
│  │     │     ├─ _ssl_compat.cpython-311.pyc
│  │     │     ├─ _url.cpython-311.pyc
│  │     │     ├─ _utils.cpython-311.pyc
│  │     │     ├─ _wsdump.cpython-311.pyc
│  │     │     └─ __init__.cpython-311.pyc
│  │     ├─ websocket_client-1.8.0.dist-info
│  │     │  ├─ entry_points.txt
│  │     │  ├─ INSTALLER
│  │     │  ├─ LICENSE
│  │     │  ├─ METADATA
│  │     │  ├─ RECORD
│  │     │  ├─ top_level.txt
│  │     │  └─ WHEEL
│  │     ├─ werkzeug
│  │     │  ├─ datastructures
│  │     │  │  ├─ accept.py
│  │     │  │  ├─ auth.py
│  │     │  │  ├─ cache_control.py
│  │     │  │  ├─ csp.py
│  │     │  │  ├─ etag.py
│  │     │  │  ├─ file_storage.py
│  │     │  │  ├─ headers.py
│  │     │  │  ├─ mixins.py
│  │     │  │  ├─ range.py
│  │     │  │  ├─ structures.py
│  │     │  │  ├─ __init__.py
│  │     │  │  └─ __pycache__
│  │     │  │     ├─ accept.cpython-311.pyc
│  │     │  │     ├─ auth.cpython-311.pyc
│  │     │  │     ├─ cache_control.cpython-311.pyc
│  │     │  │     ├─ csp.cpython-311.pyc
│  │     │  │     ├─ etag.cpython-311.pyc
│  │     │  │     ├─ file_storage.cpython-311.pyc
│  │     │  │     ├─ headers.cpython-311.pyc
│  │     │  │     ├─ mixins.cpython-311.pyc
│  │     │  │     ├─ range.cpython-311.pyc
│  │     │  │     ├─ structures.cpython-311.pyc
│  │     │  │     └─ __init__.cpython-311.pyc
│  │     │  ├─ debug
│  │     │  │  ├─ console.py
│  │     │  │  ├─ repr.py
│  │     │  │  ├─ shared
│  │     │  │  │  ├─ console.png
│  │     │  │  │  ├─ debugger.js
│  │     │  │  │  ├─ ICON_LICENSE.md
│  │     │  │  │  ├─ less.png
│  │     │  │  │  ├─ more.png
│  │     │  │  │  └─ style.css
│  │     │  │  ├─ tbtools.py
│  │     │  │  ├─ __init__.py
│  │     │  │  └─ __pycache__
│  │     │  │     ├─ console.cpython-311.pyc
│  │     │  │     ├─ repr.cpython-311.pyc
│  │     │  │     ├─ tbtools.cpython-311.pyc
│  │     │  │     └─ __init__.cpython-311.pyc
│  │     │  ├─ exceptions.py
│  │     │  ├─ formparser.py
│  │     │  ├─ http.py
│  │     │  ├─ local.py
│  │     │  ├─ middleware
│  │     │  │  ├─ dispatcher.py
│  │     │  │  ├─ http_proxy.py
│  │     │  │  ├─ lint.py
│  │     │  │  ├─ profiler.py
│  │     │  │  ├─ proxy_fix.py
│  │     │  │  ├─ shared_data.py
│  │     │  │  ├─ __init__.py
│  │     │  │  └─ __pycache__
│  │     │  │     ├─ dispatcher.cpython-311.pyc
│  │     │  │     ├─ http_proxy.cpython-311.pyc
│  │     │  │     ├─ lint.cpython-311.pyc
│  │     │  │     ├─ profiler.cpython-311.pyc
│  │     │  │     ├─ proxy_fix.cpython-311.pyc
│  │     │  │     ├─ shared_data.cpython-311.pyc
│  │     │  │     └─ __init__.cpython-311.pyc
│  │     │  ├─ py.typed
│  │     │  ├─ routing
│  │     │  │  ├─ converters.py
│  │     │  │  ├─ exceptions.py
│  │     │  │  ├─ map.py
│  │     │  │  ├─ matcher.py
│  │     │  │  ├─ rules.py
│  │     │  │  ├─ __init__.py
│  │     │  │  └─ __pycache__
│  │     │  │     ├─ converters.cpython-311.pyc
│  │     │  │     ├─ exceptions.cpython-311.pyc
│  │     │  │     ├─ map.cpython-311.pyc
│  │     │  │     ├─ matcher.cpython-311.pyc
│  │     │  │     ├─ rules.cpython-311.pyc
│  │     │  │     └─ __init__.cpython-311.pyc
│  │     │  ├─ sansio
│  │     │  │  ├─ http.py
│  │     │  │  ├─ multipart.py
│  │     │  │  ├─ request.py
│  │     │  │  ├─ response.py
│  │     │  │  ├─ utils.py
│  │     │  │  ├─ __init__.py
│  │     │  │  └─ __pycache__
│  │     │  │     ├─ http.cpython-311.pyc
│  │     │  │     ├─ multipart.cpython-311.pyc
│  │     │  │     ├─ request.cpython-311.pyc
│  │     │  │     ├─ response.cpython-311.pyc
│  │     │  │     ├─ utils.cpython-311.pyc
│  │     │  │     └─ __init__.cpython-311.pyc
│  │     │  ├─ security.py
│  │     │  ├─ serving.py
│  │     │  ├─ test.py
│  │     │  ├─ testapp.py
│  │     │  ├─ urls.py
│  │     │  ├─ user_agent.py
│  │     │  ├─ utils.py
│  │     │  ├─ wrappers
│  │     │  │  ├─ request.py
│  │     │  │  ├─ response.py
│  │     │  │  ├─ __init__.py
│  │     │  │  └─ __pycache__
│  │     │  │     ├─ request.cpython-311.pyc
│  │     │  │     ├─ response.cpython-311.pyc
│  │     │  │     └─ __init__.cpython-311.pyc
│  │     │  ├─ wsgi.py
│  │     │  ├─ _internal.py
│  │     │  ├─ _reloader.py
│  │     │  ├─ __init__.py
│  │     │  └─ __pycache__
│  │     │     ├─ exceptions.cpython-311.pyc
│  │     │     ├─ formparser.cpython-311.pyc
│  │     │     ├─ http.cpython-311.pyc
│  │     │     ├─ local.cpython-311.pyc
│  │     │     ├─ security.cpython-311.pyc
│  │     │     ├─ serving.cpython-311.pyc
│  │     │     ├─ test.cpython-311.pyc
│  │     │     ├─ testapp.cpython-311.pyc
│  │     │     ├─ urls.cpython-311.pyc
│  │     │     ├─ user_agent.cpython-311.pyc
│  │     │     ├─ utils.cpython-311.pyc
│  │     │     ├─ wsgi.cpython-311.pyc
│  │     │     ├─ _internal.cpython-311.pyc
│  │     │     ├─ _reloader.cpython-311.pyc
│  │     │     └─ __init__.cpython-311.pyc
│  │     ├─ werkzeug-3.1.3.dist-info
│  │     │  ├─ INSTALLER
│  │     │  ├─ LICENSE.txt
│  │     │  ├─ METADATA
│  │     │  ├─ RECORD
│  │     │  └─ WHEEL
│  │     ├─ wsproto
│  │     │  ├─ connection.py
│  │     │  ├─ events.py
│  │     │  ├─ extensions.py
│  │     │  ├─ frame_protocol.py
│  │     │  ├─ handshake.py
│  │     │  ├─ py.typed
│  │     │  ├─ typing.py
│  │     │  ├─ utilities.py
│  │     │  ├─ __init__.py
│  │     │  └─ __pycache__
│  │     │     ├─ connection.cpython-311.pyc
│  │     │     ├─ events.cpython-311.pyc
│  │     │     ├─ extensions.cpython-311.pyc
│  │     │     ├─ frame_protocol.cpython-311.pyc
│  │     │     ├─ handshake.cpython-311.pyc
│  │     │     ├─ typing.cpython-311.pyc
│  │     │     ├─ utilities.cpython-311.pyc
│  │     │     └─ __init__.cpython-311.pyc
│  │     ├─ wsproto-1.2.0.dist-info
│  │     │  ├─ INSTALLER
│  │     │  ├─ LICENSE
│  │     │  ├─ METADATA
│  │     │  ├─ RECORD
│  │     │  ├─ top_level.txt
│  │     │  └─ WHEEL
│  │     ├─ _cffi_backend.cp311-win_amd64.pyd
│  │     ├─ _distutils_hack
│  │     │  ├─ override.py
│  │     │  ├─ __init__.py
│  │     │  └─ __pycache__
│  │     │     ├─ override.cpython-311.pyc
│  │     │     └─ __init__.cpython-311.pyc
│  │     └─ __pycache__
│  │        ├─ socks.cpython-311.pyc
│  │        ├─ sockshandler.cpython-311.pyc
│  │        └─ typing_extensions.cpython-311.pyc
│  ├─ pyvenv.cfg
│  └─ Scripts
│     ├─ activate
│     ├─ activate.bat
│     ├─ Activate.ps1
│     ├─ deactivate.bat
│     ├─ dotenv.exe
│     ├─ flask.exe
│     ├─ gunicorn.exe
│     ├─ normalizer.exe
│     ├─ pip.exe
│     ├─ pip3.11.exe
│     ├─ pip3.exe
│     ├─ python.exe
│     ├─ pythonw.exe
│     └─ wsdump.exe
└─ __pycache__
   ├─ app.cpython-39.pyc
   └─ models.cpython-39.pyc

```