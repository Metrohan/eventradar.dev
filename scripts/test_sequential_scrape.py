import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.scrapers import (
    scrape_techcareer_events,
    scrape_coderspace_events,
    scrape_anbean_events,
    scrape_kodluyoruz_events,
    scrape_youthall_events
)
from app.services.scraper_service import process_scraped_events

print("=== SEQUENTIAL SCRAPER TEST ===\n")

print("1. Kodluyoruz...")
kod_ev = scrape_kodluyoruz_events()
print(f"   {len(kod_ev)} events\n")

print("2. Anbean...")
anb_ev = scrape_anbean_events()
print(f"   {len(anb_ev)} events\n")

print("3. TechCareer...")
tc_ev = scrape_techcareer_events()
print(f"   {len(tc_ev)} events\n")

print("4. Youthall...")
yh_ev = scrape_youthall_events()
print(f"   {len(yh_ev)} events")
for e in yh_ev[:3]:
    print(f"   - {e['title'][:50]}")
print()

print("5. Coderspace...")
cs_ev = scrape_coderspace_events()
print(f"   {len(cs_ev)} events\n")

all_events = kod_ev + anb_ev + tc_ev + yh_ev + cs_ev
print(f"\nTOTAL: {len(all_events)} events")

if all_events:
    print("\nSaving to DB...")
    result = process_scraped_events(all_events, "Test Run")
    print(f"Result: {result}")
