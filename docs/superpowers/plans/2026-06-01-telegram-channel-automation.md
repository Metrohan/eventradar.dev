# Telegram Kanal Otomasyonu — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Scraper yeni etkinlik kaydettiğinde Telegram kanalına zengin formatlı anlık bildirim, her sabah günlük özet ve her Pazartesi haftalık özet gönder.

**Architecture:** `app/services/telegram_service.py` tüm Telegram mantığını (formatlama + gönderim) barındırır. `process_scraped_events` yeni kayıtları bu servise iletir. İki bağımsız script günlük/haftalık özet için DB'yi sorgular ve servisi çağırır.

**Tech Stack:** Python `requests` (zaten mevcut), Telegram Bot API (sendMessage + sendPhoto), pytest + unittest.mock, SQLAlchemy (mevcut)

---

## Dosya Haritası

| Dosya | İşlem | Sorumluluk |
|---|---|---|
| `app/services/telegram_service.py` | Oluştur | Mesaj formatlama + Telegram API gönderimi |
| `app/services/scraper_service.py` | Değiştir | `process_scraped_events` içine Telegram hook'u ekle |
| `scripts/send_daily_digest.py` | Oluştur | Günlük özet cron scripti |
| `scripts/send_weekly_digest.py` | Oluştur | Haftalık özet cron scripti |
| `tests/unit/test_telegram_service.py` | Oluştur | Servis unit testleri |
| `.env.example` | Değiştir | `TELEGRAM_CHANNEL_ID` satırı ekle |

---

## Task 1: `telegram_service.py` — Temel Gönderim + Formatlama

**Files:**
- Create: `app/services/telegram_service.py`
- Create: `tests/unit/test_telegram_service.py`

- [ ] **Step 1: Test dosyasını oluştur — `_is_configured` ve `_format_event_message` testleri**

```python
# tests/unit/test_telegram_service.py
import os
os.environ.setdefault("ALLOW_INSECURE_DEFAULTS", "true")
os.environ.setdefault("SECRET_KEY", "test-secret-key-that-is-at-least-32-chars")
os.environ.setdefault("ADMIN_USERNAME", "testadmin")
os.environ.setdefault("ADMIN_PASSWORD", "testpassword")

import pytest
from unittest.mock import patch, MagicMock


def test_not_configured_when_env_missing(monkeypatch):
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.delenv("TELEGRAM_CHANNEL_ID", raising=False)
    # reload so module picks up env changes
    import importlib
    import app.services.telegram_service as ts
    importlib.reload(ts)
    assert ts._is_configured() is False


def test_configured_when_both_env_set(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123:ABC")
    monkeypatch.setenv("TELEGRAM_CHANNEL_ID", "@testchannel")
    import importlib
    import app.services.telegram_service as ts
    importlib.reload(ts)
    assert ts._is_configured() is True


def test_format_event_message_contains_title():
    import importlib
    import app.services.telegram_service as ts
    importlib.reload(ts)
    event = {
        "title": "KKB Hackathon",
        "url": "https://coderspace.io/etkinlikler/kkb/",
        "source": "Coderspace",
        "date": "16 November 2026",
        "description": "Yapay zeka hackathonu.",
        "image_url": "",
    }
    msg = ts._format_event_message(event)
    assert "KKB Hackathon" in msg
    assert "Coderspace" in msg
    assert "https://coderspace.io/etkinlikler/kkb/" in msg


def test_format_event_message_truncates_long_description():
    import importlib
    import app.services.telegram_service as ts
    importlib.reload(ts)
    event = {
        "title": "Test Event",
        "url": "https://example.com",
        "source": "Test",
        "date": "",
        "description": "A" * 300,
        "image_url": "",
    }
    msg = ts._format_event_message(event)
    assert "..." in msg
    # description portion should be <= 203 chars (200 + "...")
    lines = msg.split("\n")
    desc_line = [l for l in lines if l.startswith("📝")]
    assert len(desc_line[0]) <= 210  # 📝 + space + 200 chars + ...


def test_detect_type():
    import importlib
    import app.services.telegram_service as ts
    importlib.reload(ts)
    assert ts._detect_type("KKB Hackathon 2026") == "hackathon"
    assert ts._detect_type("Python Bootcamp Istanbul") == "bootcamp"
    assert ts._detect_type("Vodafone Staj Programı") == "staj"
    assert ts._detect_type("AI Webinar Serisi") == "seminer"
    assert ts._detect_type("Teknoloji Zirvesi") == "diğer"
```

- [ ] **Step 2: Testleri çalıştır — başarısız olduklarını doğrula**

```bash
docker compose exec -T backend pytest tests/unit/test_telegram_service.py -v 2>&1 | head -30
```

Beklenen: `ModuleNotFoundError: No module named 'app.services.telegram_service'`

- [ ] **Step 3: `telegram_service.py` dosyasını oluştur**

```python
# app/services/telegram_service.py
import logging
import os
import time
from typing import Optional

import requests

logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHANNEL_ID: str = os.getenv("TELEGRAM_CHANNEL_ID", "")

_TYPE_EMOJIS = {
    "hackathon": "🏆",
    "bootcamp": "🎓",
    "staj": "💼",
    "seminer": "📚",
    "konferans": "🎤",
    "atolye": "🔧",
    "diğer": "📌",
}


def _is_configured() -> bool:
    """Bot token ve kanal ID'si tanımlanmışsa True döner."""
    return bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHANNEL_ID)


def _detect_type(title: str) -> str:
    """Başlıktan etkinlik türünü tahmin eder."""
    t = title.lower()
    if any(k in t for k in ("hackathon", "datathon", "ideathon")):
        return "hackathon"
    if "bootcamp" in t:
        return "bootcamp"
    if any(k in t for k in ("staj", "internship")):
        return "staj"
    if any(k in t for k in ("webinar", "seminer", "seminar", "söyleşi")):
        return "seminer"
    if any(k in t for k in ("konferans", "summit", "zirve")):
        return "konferans"
    if any(k in t for k in ("atölye", "workshop")):
        return "atolye"
    return "diğer"


def _format_event_message(event: dict) -> str:
    """Tek etkinlik için zengin formatlı HTML mesajı oluşturur."""
    title = event.get("title", "")
    url = event.get("url", "")
    source = event.get("source", "")
    date_str = event.get("date", "")
    description = event.get("description", "")

    if description and len(description) > 200:
        description = description[:197] + "..."

    event_type = _detect_type(title)
    type_emoji = _TYPE_EMOJIS.get(event_type, "📌")

    lines = [
        "🔔 <b>Yeni Etkinlik</b>",
        "",
        f"📌 <b>{title}</b>",
        f"{type_emoji} {event_type.title()} · {source}",
    ]
    if date_str:
        lines.append(f"📅 {date_str}")
    if description:
        lines.append(f"📝 {description}")
    lines.extend(["", f'🔗 <a href="{url}">Detaylar →</a>'])

    return "\n".join(lines)


def _send_message(text: str) -> bool:
    """Kanala metin mesajı gönderir. Başarılıysa True döner."""
    if not _is_configured():
        return False
    api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        resp = requests.post(
            api_url,
            json={
                "chat_id": TELEGRAM_CHANNEL_ID,
                "text": text,
                "parse_mode": "HTML",
                "disable_web_page_preview": False,
            },
            timeout=10,
        )
        resp.raise_for_status()
        return True
    except Exception as exc:
        logger.error(f"Telegram sendMessage hatası: {exc}")
        return False


def _send_photo(image_url: str, caption: str) -> bool:
    """Kanala görsel + açıklama gönderir. Başarısız olursa False döner."""
    if not _is_configured():
        return False
    api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    try:
        resp = requests.post(
            api_url,
            json={
                "chat_id": TELEGRAM_CHANNEL_ID,
                "photo": image_url,
                "caption": caption,
                "parse_mode": "HTML",
            },
            timeout=10,
        )
        resp.raise_for_status()
        return True
    except Exception as exc:
        logger.warning(f"Telegram sendPhoto başarısız, metin mesajına geçiliyor: {exc}")
        return False


def notify_new_events(events: list[dict]) -> None:
    """
    Yeni etkinlikler için anlık bildirim gönderir.
    Görsel varsa sendPhoto, yoksa sendMessage kullanır.
    Birden fazla etkinlikte mesajlar arası 0.5s beklenir.
    """
    if not _is_configured() or not events:
        return

    for i, event in enumerate(events):
        text = _format_event_message(event)
        image_url = event.get("image_url", "")

        if image_url:
            success = _send_photo(image_url, text)
            if not success:
                _send_message(text)
        else:
            _send_message(text)

        if i < len(events) - 1:
            time.sleep(0.5)


def send_daily_digest(events: list[dict], date_label: str) -> None:
    """
    Günlük özet gönderir. events boşsa hiçbir şey göndermez.
    date_label: "1 Haziran 2026" formatında string.
    """
    if not _is_configured() or not events:
        return

    lines = [f"📊 <b>Günlük Özet · {date_label}</b>", ""]
    lines.append(f"Bugün <b>{len(events)}</b> yeni etkinlik eklendi:")
    lines.append("")

    for event in events[:10]:
        title = event.get("title", "")
        url = event.get("url", "")
        lines.append(f'• <a href="{url}">{title}</a>')

    if len(events) > 10:
        lines.append(f"  … ve {len(events) - 10} etkinlik daha")

    lines.extend(["", '👉 <a href="https://eventradar.dev">eventradar.dev</a>'])
    _send_message("\n".join(lines))


def send_weekly_digest(events: list[dict], week_label: str) -> None:
    """
    Haftalık özet gönderir. events boş olsa bile gönderir.
    week_label: "26 Mayıs – 1 Haziran" formatında string.
    """
    if not _is_configured():
        return

    if not events:
        _send_message(
            f"📅 <b>Haftalık Özet · {week_label}</b>\n\n"
            "Bu hafta yeni etkinlik eklenmedi.\n\n"
            '👉 <a href="https://eventradar.dev">eventradar.dev</a>'
        )
        return

    from collections import Counter
    type_counts: Counter = Counter(_detect_type(e.get("title", "")) for e in events)

    lines = [f"📅 <b>Haftalık Özet · {week_label}</b>", ""]
    lines.append(f"Bu hafta <b>{len(events)}</b> etkinlik eklendi:")

    type_parts = []
    for etype, count in type_counts.most_common(4):
        emoji = _TYPE_EMOJIS.get(etype, "📌")
        type_parts.append(f"{emoji} {count} {etype.title()}")
    if type_parts:
        lines.append("   ".join(type_parts))

    lines.extend(["", '👉 <a href="https://eventradar.dev">eventradar.dev</a>'])
    _send_message("\n".join(lines))
```

- [ ] **Step 4: Testleri çalıştır — geçtiklerini doğrula**

```bash
docker compose exec -T backend pytest tests/unit/test_telegram_service.py -v
```

Beklenen: 7 test PASS

- [ ] **Step 5: Commit**

```bash
git add app/services/telegram_service.py tests/unit/test_telegram_service.py
git commit -m "feat: telegram_service — mesaj formatlama ve gönderim"
```

---

## Task 2: `notify_new_events` için ek testler + `_send_message` mock

**Files:**
- Modify: `tests/unit/test_telegram_service.py`

- [ ] **Step 1: Test dosyasına mock testleri ekle**

```python
# tests/unit/test_telegram_service.py dosyasına ekle (mevcut testlerin altına)

def test_send_message_calls_requests_post(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123:ABC")
    monkeypatch.setenv("TELEGRAM_CHANNEL_ID", "@ch")
    import importlib
    import app.services.telegram_service as ts
    importlib.reload(ts)

    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None

    with patch("app.services.telegram_service.requests.post", return_value=mock_resp) as mock_post:
        result = ts._send_message("test mesajı")

    assert result is True
    mock_post.assert_called_once()
    call_kwargs = mock_post.call_args
    assert "test mesajı" in str(call_kwargs)
    assert "HTML" in str(call_kwargs)


def test_send_message_returns_false_when_not_configured(monkeypatch):
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.delenv("TELEGRAM_CHANNEL_ID", raising=False)
    import importlib
    import app.services.telegram_service as ts
    importlib.reload(ts)
    result = ts._send_message("test")
    assert result is False


def test_notify_new_events_noop_when_empty(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123:ABC")
    monkeypatch.setenv("TELEGRAM_CHANNEL_ID", "@ch")
    import importlib
    import app.services.telegram_service as ts
    importlib.reload(ts)

    with patch("app.services.telegram_service._send_message") as mock_send:
        ts.notify_new_events([])
    mock_send.assert_not_called()


def test_notify_new_events_sends_per_event(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123:ABC")
    monkeypatch.setenv("TELEGRAM_CHANNEL_ID", "@ch")
    import importlib
    import app.services.telegram_service as ts
    importlib.reload(ts)

    events = [
        {"title": "A", "url": "https://a.com", "source": "S", "date": "", "description": "", "image_url": ""},
        {"title": "B", "url": "https://b.com", "source": "S", "date": "", "description": "", "image_url": ""},
    ]
    with patch("app.services.telegram_service._send_message") as mock_send, \
         patch("app.services.telegram_service.time.sleep") as mock_sleep:
        ts.notify_new_events(events)

    assert mock_send.call_count == 2
    mock_sleep.assert_called_once_with(0.5)


def test_send_daily_digest_noop_when_empty(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123:ABC")
    monkeypatch.setenv("TELEGRAM_CHANNEL_ID", "@ch")
    import importlib
    import app.services.telegram_service as ts
    importlib.reload(ts)

    with patch("app.services.telegram_service._send_message") as mock_send:
        ts.send_daily_digest([], "1 Haziran 2026")
    mock_send.assert_not_called()


def test_send_weekly_digest_sends_even_when_empty(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123:ABC")
    monkeypatch.setenv("TELEGRAM_CHANNEL_ID", "@ch")
    import importlib
    import app.services.telegram_service as ts
    importlib.reload(ts)

    with patch("app.services.telegram_service._send_message") as mock_send:
        ts.send_weekly_digest([], "26 Mayıs – 1 Haziran")

    mock_send.assert_called_once()
    assert "yeni etkinlik eklenmedi" in mock_send.call_args[0][0]
```

- [ ] **Step 2: Testleri çalıştır**

```bash
docker compose exec -T backend pytest tests/unit/test_telegram_service.py -v
```

Beklenen: 14 test PASS

- [ ] **Step 3: Commit**

```bash
git add tests/unit/test_telegram_service.py
git commit -m "test: telegram_service mock testleri ekle"
```

---

## Task 3: `scraper_service.py` — yeni etkinlik hook'u

**Files:**
- Modify: `app/services/scraper_service.py:175-240`

- [ ] **Step 1: `process_scraped_events` içinde yeni etkinlikleri topla**

`app/services/scraper_service.py` dosyasında `process_scraped_events` fonksiyonunu bul. `now = datetime.now()` satırından hemen sonra ve `for data in events_data:` döngüsü içindeki `new_count += 1` satırından sonra değişiklik yap:

`now = datetime.now()` satırının hemen altına ekle:
```python
        new_event_data: list[dict] = []
```

`new_count += 1` satırının hemen altına (yeni etkinlik oluşturan `else` bloğunda) ekle:
```python
                    new_event_data.append(data)
```

`db.commit()` satırından **sonra**, `result = f"New: ..."` satırından **önce** ekle:
```python
        # Telegram bildirimi — fire-and-forget, scrape akışını kesmez
        if new_event_data:
            try:
                from .telegram_service import notify_new_events
                notify_new_events(new_event_data)
            except Exception as tg_err:
                print(f"Telegram bildirimi gönderilemedi (non-fatal): {tg_err}")
```

- [ ] **Step 2: Mevcut scraper_service testlerinin hâlâ geçtiğini doğrula**

```bash
docker compose exec -T backend pytest tests/unit/test_scraper_service.py -v
```

Beklenen: tüm testler PASS

- [ ] **Step 3: Commit**

```bash
git add app/services/scraper_service.py
git commit -m "feat: scraper_service — yeni etkinlikte Telegram hook ekle"
```

---

## Task 4: Günlük özet scripti

**Files:**
- Create: `scripts/send_daily_digest.py`

- [ ] **Step 1: Scripti oluştur**

```python
#!/usr/bin/env python3
"""
Bir önceki günde eklenen etkinliklerin özetini Telegram kanalına gönderir.
Cron: her sabah 09:00
  0 9 * * * cd ~/TechEventRadar && docker compose exec -T backend python scripts/send_daily_digest.py >> ~/scrape.log 2>&1
"""
import os
import sys
from datetime import datetime, timedelta

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.insert(0, project_root)

from app.core.database import SessionLocal
from app.models.event import Event
from app.services.telegram_service import send_daily_digest


def main() -> None:
    db = SessionLocal()
    try:
        yesterday_start = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        ) - timedelta(days=1)
        yesterday_end = yesterday_start + timedelta(days=1)

        events = (
            db.query(Event)
            .filter(
                Event.is_active == True,
                Event.scraped_at >= yesterday_start,
                Event.scraped_at < yesterday_end,
            )
            .order_by(Event.scraped_at.desc())
            .all()
        )

        event_dicts = [
            {"title": e.title, "url": e.url, "source": e.source}
            for e in events
        ]

        date_label = yesterday_start.strftime("%-d %B %Y")
        send_daily_digest(event_dicts, date_label)

        if event_dicts:
            print(f"Günlük özet gönderildi: {len(event_dicts)} etkinlik ({date_label})")
        else:
            print(f"Günlük özet atlandı: dün ({date_label}) yeni etkinlik yok")
    finally:
        db.close()


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Container içinde çalıştığını test et**

```bash
cd ~/TechEventRadar && docker compose exec -T backend python scripts/send_daily_digest.py
```

Beklenen çıktı: `Günlük özet atlandı: dün ...` veya `Günlük özet gönderildi: N etkinlik`
(TELEGRAM_CHANNEL_ID henüz set edilmemişse sessizce tamamlanır)

- [ ] **Step 3: Commit**

```bash
git add scripts/send_daily_digest.py
git commit -m "feat: send_daily_digest.py — günlük özet cron scripti"
```

---

## Task 5: Haftalık özet scripti

**Files:**
- Create: `scripts/send_weekly_digest.py`

- [ ] **Step 1: Scripti oluştur**

```python
#!/usr/bin/env python3
"""
Son 7 günde eklenen etkinliklerin özetini Telegram kanalına gönderir.
Etkinlik olmasa bile her Pazartesi gönderilir.
Cron: her Pazartesi 09:00
  0 9 * * 1 cd ~/TechEventRadar && docker compose exec -T backend python scripts/send_weekly_digest.py >> ~/scrape.log 2>&1
"""
import os
import sys
from datetime import datetime, timedelta

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.insert(0, project_root)

from app.core.database import SessionLocal
from app.models.event import Event
from app.services.telegram_service import send_weekly_digest


def main() -> None:
    db = SessionLocal()
    try:
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today - timedelta(days=7)

        events = (
            db.query(Event)
            .filter(
                Event.is_active == True,
                Event.scraped_at >= week_start,
                Event.scraped_at < today,
            )
            .order_by(Event.scraped_at.desc())
            .all()
        )

        event_dicts = [
            {"title": e.title, "url": e.url, "source": e.source}
            for e in events
        ]

        week_label = (
            f"{week_start.strftime('%-d %B')} – {(today - timedelta(days=1)).strftime('%-d %B')}"
        )
        send_weekly_digest(event_dicts, week_label)

        print(f"Haftalık özet gönderildi: {len(event_dicts)} etkinlik ({week_label})")
    finally:
        db.close()


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Container içinde çalıştığını test et**

```bash
cd ~/TechEventRadar && docker compose exec -T backend python scripts/send_weekly_digest.py
```

Beklenen: `Haftalık özet gönderildi: N etkinlik (...)` — hata yok

- [ ] **Step 3: Commit**

```bash
git add scripts/send_weekly_digest.py
git commit -m "feat: send_weekly_digest.py — haftalık özet cron scripti"
```

---

## Task 6: `.env.example` güncelle + crontab ekle

**Files:**
- Modify: `.env.example`

- [ ] **Step 1: `.env.example`'a `TELEGRAM_CHANNEL_ID` ekle**

`.env.example` dosyasında `TELEGRAM_BOT_TOKEN` satırını bul ve hemen altına ekle:

```
TELEGRAM_CHANNEL_ID=@kanal_adi_buraya   # veya negatif sayısal kanal ID'si
```

- [ ] **Step 2: Sunucuda `.env` dosyasını güncelle**

```bash
# Sunucuda çalıştır:
echo "TELEGRAM_CHANNEL_ID=@kanal_adi_buraya" >> ~/TechEventRadar/.env
```

Gerçek kanal ID'sini `@kanal_adi_buraya` yerine yaz. Kanal ID'sini bulmak için: kanala `@userinfobot` ekle veya kanala mesaj at ve `https://api.telegram.org/bot<TOKEN>/getUpdates` ile kontrol et.

- [ ] **Step 3: Crontab'a özet satırlarını ekle**

```bash
crontab -e
```

Şu satırları ekle (mevcut `0 5 * * *` satırının altına):

```cron
# Günlük özet — her sabah 09:00
0 9 * * * cd ~/TechEventRadar && /usr/bin/docker compose exec -T backend python scripts/send_daily_digest.py >> ~/scrape.log 2>&1

# Haftalık özet — her Pazartesi 09:00
0 9 * * 1 cd ~/TechEventRadar && /usr/bin/docker compose exec -T backend python scripts/send_weekly_digest.py >> ~/scrape.log 2>&1
```

- [ ] **Step 4: Commit**

```bash
git add .env.example
git commit -m "chore: TELEGRAM_CHANNEL_ID env değişkeni ekle"
```

---

## Task 7: Uçtan uca test

- [ ] **Step 1: Tüm unit testlerin geçtiğini doğrula**

```bash
cd ~/TechEventRadar && docker compose exec -T backend pytest tests/unit/ -v --tb=short 2>&1 | tail -20
```

Beklenen: tüm testler PASS, 0 FAIL

- [ ] **Step 2: Telegram bot'unu kanala ekle**

1. Telegram'da yeni public kanal oluştur (örn. `@eventradar_tr`)
2. Bot'u kanalın admin'i yap (Mesaj Gönder yetkisi yeterli)
3. `.env`'deki `TELEGRAM_CHANNEL_ID` değerini güncelle
4. Container'ı yeniden başlat: `docker compose down && docker compose up -d`

- [ ] **Step 3: Haftalık özeti manuel tetikle**

```bash
cd ~/TechEventRadar && docker compose exec -T backend python scripts/send_weekly_digest.py
```

Beklenen: Telegram kanalında özet mesajı görünür.

- [ ] **Step 4: Tek etkinlikle anlık bildirimi test et**

```bash
cd ~/TechEventRadar && docker compose exec -T backend python3 -c "
import sys; sys.path.insert(0, '.')
from app.services.telegram_service import notify_new_events
notify_new_events([{
    'title': 'Test Etkinliği',
    'url': 'https://eventradar.dev',
    'source': 'Coderspace',
    'date': '15 Haziran 2026',
    'description': 'Bu bir test bildirimidir.',
    'image_url': '',
}])
print('Gönderildi')
"
```

Beklenen: Telegram kanalında "🔔 Yeni Etkinlik" mesajı görünür.

- [ ] **Step 5: Son commit**

```bash
git add -A
git commit -m "feat: Telegram kanal otomasyonu tamamlandı (anlık bildirim + günlük/haftalık özet)"
```
