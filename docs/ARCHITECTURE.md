# Architecture

## Database Schema

```text
Events
├── id (PK)
├── title (String 500, NOT NULL)
├── description (Text, nullable)
├── date (DateTime, nullable)
├── location (String 255, nullable)
├── url (String 500, UNIQUE, NOT NULL)
├── image_url (String 500, nullable)
├── source (String 100, NOT NULL)
├── is_active (Boolean, default True)
└── scraped_at (DateTime)

ScraperLogs
├── id (PK)
├── source (String 100)
├── status ('success' | 'failed')
├── events_found (Integer)
├── new_events (Integer)
├── error_message (Text, nullable)
├── duration_seconds (Float)
└── created_at (DateTime)

Subscribers
├── id (PK)
├── contact_info (String 255)  -- email or Telegram chat_id
├── channel ('email' | 'telegram')
├── interests (JSON list)
├── is_active (Boolean)
└── created_at (DateTime)
```

## Key API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | /api/events | — | List events (filterable) |
| GET | /health | — | Health check |
| POST | /api/admin/login | — | Get JWT token |
| GET | /api/admin/events | JWT | All events |
| POST | /api/admin/events | JWT | Create event |
| GET | /api/admin/quality | JWT | Data quality dashboard |
| GET | /api/admin/scraper-logs | JWT | Recent scraper logs |
| POST | /api/admin/broadcast | JWT | Send notifications |

## Scraper Flow

1. Admin triggers via `/api/admin/scrape/{source}` or cron script
2. `ScraperService._run_scraper_task(source)` calls the matching function
3. Scraper returns `List[Dict]` — each dict has title, url, source, etc.
4. `EventService` upserts by URL (update if exists, insert if new)
5. `ScraperLog` row written with status, count, duration
6. Admin can view results at `/api/admin/quality`

## Notification Flow

1. Admin calls `POST /api/admin/broadcast` with message + target_channel
2. `NotificationService.broadcast_message()` queries active subscribers
3. Per subscriber: `_send_email()` (SMTP) or `_send_telegram()` (Bot API)
4. In DEBUG mode (`DEBUG=true` or `SMTP_HOST` empty), both methods log to console instead of sending
