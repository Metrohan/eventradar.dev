import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.scrapers.youthall_scraper import scrape_youthall_events

print("Testing Youthall with new options...")
ev = scrape_youthall_events()
print(f'\nResult: {len(ev)} events')

for i, e in enumerate(ev[:3]):
    print(f"  [{i+1}] {e['title'][:60]}")
    print(f"      URL: {e['url'][:70]}")
    print(f"      Date: {e['date']}")
