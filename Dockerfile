FROM python:3.11-slim

# Uygulama dizinini oluştur ve içine gir
WORKDIR /app

# Chrome ve Selenium için sistem bağımlılıklarını kur
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    gnupg \
    unzip \
    postgresql-client \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libwayland-client0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xdg-utils \
    ca-certificates \
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# requirements.txt dosyasını kopyala ve bağımlılıkları yükle
# Bu adım, requirements.txt değiştiğinde yeniden çalışır.
COPY requirements.txt constraints.txt ./
RUN pip install --no-cache-dir -r requirements.txt -c constraints.txt

# Run as an unprivileged user (this container drives Chrome against third-party pages).
# The code stays root-owned/read-only for it; only HOME (webdriver/uc caches) and the
# data dir (thumbnails volume) are writable. Existing root-owned volumes are fixed by the
# `chown` step in .github/workflows/deploy.yml.
RUN groupadd --system --gid 10001 app \
    && useradd --system --uid 10001 --gid app --create-home --home-dir /home/app --shell /usr/sbin/nologin app \
    && mkdir -p /app/data/thumbnails \
    && chown -R app:app /app/data

COPY alembic/ alembic/
COPY alembic.ini .
COPY app/ app/
COPY scripts/ scripts/

# COPY keeps the source modes; a checkout made under a restrictive umask (the production
# server has app/ and scripts/ at 0700) would leave the code unreadable for `app`.
RUN chmod -R a+rX /app/alembic /app/alembic.ini /app/app /app/scripts

USER app
ENV HOME=/home/app

EXPOSE 8000

ENV PATH="/usr/bin:/usr/local/bin:$PATH"
ENV CHROME_BIN=/usr/bin/google-chrome-stable
ENV CHROMEDRIVER_PATH=/usr/local/bin/chromedriver

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]