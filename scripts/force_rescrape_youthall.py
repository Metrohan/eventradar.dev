from app.core.database import SessionLocal
from app.models.event import Event
from app.services.event_service import EventService
from app.scrapers.youthall_scraper import scrape_youthall_events

db = SessionLocal()
service = EventService(db)

# 1. Delete existing Youthall events
print("Deleting existing Youthall events...")
youthall_events = db.query(Event).filter(Event.source == "Youthall").all()
for e in youthall_events:
    db.delete(e)
db.commit()
print(f"Deleted {len(youthall_events)} events.")

# 2. Re-scrape
print("Rescraping Youthall...")
events_data = scrape_youthall_events()
print(f"Found {len(events_data)} new events.")

# 3. Save new events
mapped_count = 0
from app.schemas.event import EventCreate
from datetime import datetime


def parse_turkish_date(date_str):
    if not date_str or "belirtilmemiş" in date_str:
        return None

    # Format: "12 Şubat Perşembe, 12:00"
    # We need to map Turkish months to numbers
    months = {
        "Ocak": 1,
        "Şubat": 2,
        "Mart": 3,
        "Nisan": 4,
        "Mayıs": 5,
        "Haziran": 6,
        "Temmuz": 7,
        "Ağustos": 8,
        "Eylül": 9,
        "Ekim": 10,
        "Kasım": 11,
        "Aralık": 12,
    }

    try:
        parts = date_str.split()
        # parts[0] = Day (12)
        # parts[1] = Month (Şubat)
        # parts[2] = Day Name (Perşembe,) - might have comma
        # parts[3] = Time (12:00)

        day = int(parts[0])
        month_name = parts[1]
        month = months.get(month_name, 1)

        # Find time component (contains :)
        time_str = "00:00"
        for p in parts:
            if ":" in p:
                time_str = p.strip(",")
                break

        hour, minute = map(int, time_str.split(":"))

        # Assume year 2026 based on user context
        year = 2026

        return datetime(year, month, day, hour, minute)
    except Exception as e:
        print(f"Date parse error for {date_str}: {e}")
        return None


for e_data in events_data:
    try:
        # Map dict to EventCreate schema if needed, or manual object creation
        # EventService expects EventCreate
        event_in = EventCreate(
            title=e_data["title"],
            description=e_data["description"],
            url=e_data["url"],
            image_url=e_data.get("image_url"),
            source=e_data["source"],
            location=e_data.get("location", "Online"),
            date=parse_turkish_date(e_data.get("date")),
            is_active=True,
        )
        service.create_event(event_in)
        mapped_count += 1
    except Exception as e:
        print(f"Error saving event {e_data['title']}: {e}")

print(f"Successfully saved {mapped_count} events.")
db.close()
