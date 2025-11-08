import sys
sys.path.insert(0, '/app')

from app.scrapers.kodluyoruz_scraper import scrape_kodluyoruz_events
from app.scrapers.anbean_scraper import scrape_anbean_events

print("=== Kodluyoruz Tarihleri ===")
kod_events = scrape_kodluyoruz_events()
for e in kod_events[:3]:
    print(f"Başlık: {e.get('title')}")
    print(f"Tarih: {e.get('date')}")
    print(f"Tür: {type(e.get('date'))}")
    print("---")

print("\n=== Anbean Tarihleri ===")
anb_events = scrape_anbean_events()
for e in anb_events[:3]:
    print(f"Başlık: {e.get('title')}")
    print(f"Tarih: {e.get('date')}")
    print(f"Tür: {type(e.get('date'))}")
    print("---")
