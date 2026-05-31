# Telegram Kanal Otomasyonu — Tasarım Dokümanı

**Tarih:** 2026-06-01  
**Durum:** Onaylandı  
**Hedef:** Yeni etkinliklerin otomatik Telegram kanalına bildirilmesi + günlük/haftalık özet

---

## Genel Bakış

TechEventRadar'ın scraperları yeni etkinlik bulduğunda otomatik olarak bir Telegram kanalına zengin formatlı mesaj gönderilir. Günlük ve haftalık özet mesajları cron ile çalışır. Bu özellik siteye ve repoya gelen trafiği artırmayı, Türk tech topluluğunda organik yayılımı hedefler.

---

## Mimari

### Yeni Bileşenler

```
app/services/telegram_service.py   — tüm Telegram gönderim mantığı
scripts/send_daily_digest.py       — günlük özet cron scripti
scripts/send_weekly_digest.py      — haftalık özet cron scripti
```

### Değişen Bileşenler

```
app/services/scraper_service.py    — process_scraped_events'e hook eklenir
.env.example                       — TELEGRAM_CHANNEL_ID eklenir
crontab (sunucu)                   — 2 yeni satır
```

### Veri Akışı

```
run_daily_scrape.py
  → process_scraped_events()
      → yeni etkinlik kaydedilir
      → telegram_service.notify_new_events(new_events) çağrılır
          → her etkinlik için sendPhoto (görsel varsa) veya sendMessage

cron 09:00 her gün
  → send_daily_digest.py
      → dün eklenen etkinlikleri DB'den çek
      → en az 1 etkinlik varsa özet gönder

cron 09:00 her Pazartesi
  → send_weekly_digest.py
      → son 7 günün etkinliklerini DB'den çek
      → özet gönder (0 olsa bile)
```

---

## Telegram Servis API'si (`telegram_service.py`)

```python
def notify_new_events(events: list[dict]) -> None
    """Yeni etkinlikler için anlık bildirim gönderir."""

def send_daily_digest(events: list[dict], date: date) -> None
    """Günlük özet mesajı gönderir. events boşsa gönderme."""

def send_weekly_digest(events: list[dict], week_start: date, week_end: date) -> None
    """Haftalık özet mesajı gönderir. Her zaman gönderir."""
```

Tüm gönderimler `requests.post` ile Telegram Bot API'ye yapılır. Hata olursa loglanır, uygulama akışı kesilmez (fire-and-forget).

---

## Mesaj Formatları

### Anlık Bildirim

```
🔔 Yeni Etkinlik

📌 KKB Hackathon: Agentic AI
🏷️ Hackathon · Coderspace
📅 Son Başvuru: 16 Kasım 2026
📝 KKB ve partnerlerinin düzenlediği yapay zeka hackathonu.

🔗 eventradar.dev/events/42
```

Etkinliğin `image_url` alanı doluysa `sendPhoto` kullanılır (görsel + caption). Boşsa `sendMessage` ile sadece metin gönderilir. HTML parse mode kullanılır (bold/italic için).

Etkinlik türü (hackathon, bootcamp, staj, seminer) `tags` tablosundan çekilir; yoksa kaynak adı yazılır.

### Günlük Özet

Yalnızca bir önceki günde eklenen yeni etkinlikler (`scraped_at >= dün 00:00 AND is_active = true`). Etkinlik yoksa mesaj gönderilmez.

```
📊 Günlük Özet · 1 Haziran 2026

Bugün 3 yeni etkinlik eklendi:

• KKB Hackathon: Agentic AI
• Veri Bilimi ve YZ Yaz Okulu
• IBM ile Kodluyoruz: CyberStart

👉 eventradar.dev
```

### Haftalık Özet

Her Pazartesi, önceki 7 günü kapsar. Etkinlik yoksa bile gönderilir ("Bu hafta yeni etkinlik eklenmedi").

```
📅 Haftalık Özet · 26 Mayıs – 1 Haziran

Bu hafta 12 etkinlik eklendi:
🏆 2 Hackathon   🎓 3 Bootcamp
💼 4 Staj        📚 3 Eğitim

⏰ En yakın deadline: Teknoloji Zirvesi (10 Haziran)

👉 eventradar.dev
```

---

## Konfigürasyon

`.env`'e eklenen değişkenler:

```
TELEGRAM_CHANNEL_ID=@eventradar_tr   # veya negatif sayısal ID
```

`TELEGRAM_BOT_TOKEN` zaten mevcut. Bot kanalda admin yetkisine sahip olmalı (mesaj gönderme izni).

---

## Hata Yönetimi

- Telegram API `4xx/5xx` döndürürse hata loglanır, scrape akışı kesilmez.
- `TELEGRAM_CHANNEL_ID` veya `TELEGRAM_BOT_TOKEN` eksikse servis sessizce devre dışı kalır (startup'ta uyarı loglanır).
- Rate limit (Telegram: saniyede 30 mesaj): birden fazla yeni etkinlik varsa mesajlar arasında 0.5s beklenir.

---

## Crontab Satırları

```cron
# Günlük özet — her sabah 09:00
0 9 * * * cd ~/TechEventRadar && /usr/bin/docker compose exec -T backend python scripts/send_daily_digest.py >> ~/scrape.log 2>&1

# Haftalık özet — her Pazartesi 09:00
0 9 * * 1 cd ~/TechEventRadar && /usr/bin/docker compose exec -T backend python scripts/send_weekly_digest.py >> ~/scrape.log 2>&1
```

---

## Kurulum Adımları (manuel, tek seferlik)

1. Telegram'da public kanal oluştur (`@eventradar_tr` veya benzeri).
2. Mevcut botu (`TELEGRAM_BOT_TOKEN`) kanala admin olarak ekle.
3. `.env`'e `TELEGRAM_CHANNEL_ID` ekle.
4. `docker-compose down && docker-compose up -d` ile yeniden başlat.
5. İlk testi manuel tetikle: `docker compose exec -T backend python scripts/send_weekly_digest.py`.

---

## Kapsam Dışı

- Twitter/LinkedIn otomasyonu (ayrı özellik)
- Kullanıcıların bireysel bot üzerinden bildirim alması (mevcut `subscribers` tablosu bunu zaten destekliyor)
- Mesaj düzenleme / silme
- Kanal istatistikleri
