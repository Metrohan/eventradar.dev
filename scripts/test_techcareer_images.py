import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.scrapers.techcareer_scraper import scrape_techcareer_events

print("=== TECHCAREER IMAGE TEST ===")
ev = scrape_techcareer_events()
print(f'TechCareer: {len(ev)} events')

for e in ev[:5]:
    print(f"\n  Title: {e['title'][:60]}")
    print(f"  Image: {e.get('image_url', 'NO IMAGE')}")
    print(f"  URL: {e['url'][:70]}")
