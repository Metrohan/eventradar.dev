from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import re
import os

from .driver_utils import ensure_chromedriver


def scrape_youthall_events():
    """Youthall scraper"""
    driver_path = ensure_chromedriver()
    if not driver_path:
        print("Youthall: ChromeDriver bulunamadı, atlanıyor")
        return []

    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument(f'--user-data-dir=/tmp/youthall_chrome_{os.getpid()}')

    service = Service(executable_path=driver_path)
    driver = None

    try:
        driver = webdriver.Chrome(service=service, options=options)
        driver.get('https://www.youthall.com/tr/events')

        time.sleep(5)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        event_cards = soup.find_all('div', class_='event-row')

        events = []
        for card in event_cards:
            try:
                title_elem = card.find('h3') or card.find('h2') or card.find('h4')
                if not title_elem:
                    continue
                title = title_elem.text.strip()

                link_elem = card.find('a', href=True)
                if not link_elem:
                    continue
                url = link_elem['href']
                if not url.startswith('http'):
                    url = 'https://www.youthall.com' + url

                date_elem = card.find('div', class_='events__content__datebox')
                date_str = date_elem.text.strip() if date_elem else None

                desc_elem = card.find('div', class_='events__content__details')
                raw_details = desc_elem.text.strip() if desc_elem else ""
                clean_details = " ".join(raw_details.split())

                date_str = date_str or "Tarih belirtilmemiş"
                location = "Online"

                match = re.search(r'^(\d{1,2}\s+\w+\s+\w+),\s*(\d{1,2}:\d{2})\s*(.*)$', clean_details)
                if match:
                    parsed_date = match.group(1)
                    parsed_time = match.group(2)
                    parsed_loc = match.group(3).strip()
                    date_str = f"{parsed_date}, {parsed_time}"
                    location = parsed_loc if parsed_loc else "Online"
                elif "Online" in clean_details:
                    location = "Online"

                description = clean_details if clean_details else "Etkinlik açıklaması mevcut değil."

                img_elem = card.find('img')
                image_url = img_elem.get('src', '') if img_elem else ''
                if image_url and not image_url.startswith('http'):
                    image_url = 'https://www.youthall.com' + image_url

                events.append({
                    'title': title,
                    'url': url,
                    'date': date_str,
                    'description': description,
                    'image_url': image_url,
                    'source': 'Youthall',
                    'location': location,
                    'is_active': True
                })

            except Exception as e:
                print(f"Youthall kart hatası: {e}")
                continue

        return events

    except Exception as e:
        print(f"Youthall genel hatası: {e}")
        import traceback
        traceback.print_exc()
        return []

    finally:
        if driver:
            driver.quit()
