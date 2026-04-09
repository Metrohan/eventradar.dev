FROM python:3.9-slim-bullseye

ENV PYTHONUNBUFFERED 1 \
    DEBIAN_FRONTEND=noninteractive \
    CHROME_MAJOR_VERSION=120

# Uygulama dizinini oluştur ve içine gir
WORKDIR /app

# Chrome ve diğer sistem bağımlılıklarını yükle
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    gnupg \
    unzip \
    fonts-liberation \
    fonts-noto-color-emoji \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libexpat1 \
    libfontconfig1 \
    libgbm1 \
    libgdk-pixbuf2.0-0 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libpangocairo-1.0-0 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libxtst6 \
    xdg-utils \
    build-essential \
    python3-dev \
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update && apt-get install -y google-chrome-stable \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# requirements.txt dosyasını kopyala ve bağımlılıkları yükle
# Bu adım, requirements.txt değiştiğinde yeniden çalışır.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Tüm uygulama kodunu kopyala
# Bu adım, herhangi bir uygulama dosyası (Python kodu, HTML, CSS vb.) değiştiğinde yeniden çalışır.
COPY . . 

ENV PATH="/usr/bin:/usr/local/bin:$PATH"
ENV WD_CHROME_PATH=/usr/bin/google-chrome