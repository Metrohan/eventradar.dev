from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Any
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from app.services.date_extractor import parse_event_date


def _opts():
    o = Options()
    o.add_argument("--headless=new")
    o.add_argument("--no-sandbox")
    o.add_argument("--disable-dev-shm-usage")
    o.add_argument("--disable-gpu")
    return o


def scrape_akbank_events() -> List[Dict[str, Any]]:
    url = "https://www.akbankgenclikakademisi.com/etkinlik-takvimi"
    base = "https://www.akbankgenclikakademisi.com"
    driver = None
    events = []
    try:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=_opts()
        )
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        cards = soup.select("div.event-item")

        for c in cards:
            title_el = c.select_one("h6.text-primary a, h6.text-primary")
            title = (
                title_el.get_text(" ", strip=True) if title_el else "Akbank Etkinliği"
            )

            a = c.select_one("h6.text-primary a[href]")
            href = a.get("href", "") if a else ""
            if href and not href.startswith("http"):
                href = base + (href if href.startswith("/") else "/" + href)
            if not href:
                href = url

            img = c.select_one("img[src]")
            image_url = img.get("src", "").strip() if img else ""
            if image_url and not image_url.startswith("http"):
                image_url = base + image_url

            raw_start = c.get("data-startdate")
            date_text = ""
            if isinstance(raw_start, str):
                dt = parse_event_date(raw_start.replace("Z", "").replace("+00:00", ""))
                if dt:
                    date_text = dt.strftime("%Y-%m-%d")
            if not date_text:
                date_text = "2099-12-31"

            events.append(
                {
                    "title": title,
                    "description": "Akbank Gençlik Akademisi etkinliği",
                    "date": date_text,
                    "location": "Online",
                    "url": href,
                    "image_url": image_url,
                    "source": "Akbank",
                    "is_active": True,
                }
            )
    except Exception as e:
        print(f"Akbank Scraper Error: {e}")
    finally:
        if driver:
            driver.quit()
    return events
