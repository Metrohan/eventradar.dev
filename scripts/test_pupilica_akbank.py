import logging
import sys
import os
import requests
from bs4 import BeautifulSoup

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.insert(0, project_root)

from scrapers.pupilica_scraper import scrape_pupilica_events
from scrapers.akbank_scraper import scrape_akbank_events

print("--- Testing Pupilica ---")
try:
    events = scrape_pupilica_events()
    print(f"Pupilica found: {len(events)}")
    for e in events:
        print(f"Title: {e['title']}")
        print(f"Date: {e['date']}")
        print(f"Location: {e['location']}")
        print(f"URL: {e['url']}")
        print("-" * 20)
    
    if len(events) == 0:
        # Debug: Fetch raw html to see structure
        print("Debugging Pupilica HTML structure...")
        resp = requests.get("https://pupilica.com/events")
        print(f"Status Code: {resp.status_code}")
        print("Sample HTML (first 500 chars):")
        print(resp.text[:500])
except Exception as e:
    print(f"Pupilica Error: {e}")

print("\n--- Testing Akbank ---")
try:
    events = scrape_akbank_events()
    print(f"Akbank found: {len(events)}")
    for e in events:
        print(f"Title: {e['title']}")
        print(f"Date: {e['date']}")
        print(f"Location: {e['location']}")
        print(f"URL: {e['url']}")
        print("-" * 20)

    if len(events) == 0:
         # Debug: Fetch raw html to see structure
        print("Debugging Akbank HTML structure...")
        resp = requests.get("https://www.akbankgenclikakademisi.com/etkinlik-takvimi")
        print(f"Status Code: {resp.status_code}")
        print("Sample HTML (first 500 chars):")
        print(resp.text[:500])
except Exception as e:
    print(f"Akbank Error: {e}")
