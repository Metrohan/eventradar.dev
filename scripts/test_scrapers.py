import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.scrapers.youthall_scraper import scrape_youthall_events
from app.scrapers.cs_scraper import scrape_coderspace_events

print("=== YOUTHALL TEST ===")
ev = scrape_youthall_events()
print(f'Youthall: {len(ev)} events')
for e in ev[:3]:
    print(f"  - {e['title'][:50]} | {e['date']} | {e['url'][:60]}")

print("\n=== CODERSPACE TEST ===")
cs_ev = scrape_coderspace_events()
print(f'Coderspace: {len(cs_ev)} events')
for e in cs_ev[:3]:
    print(f"  - {e['title'][:50]} | {e['date']} | {e['url'][:60]}")
