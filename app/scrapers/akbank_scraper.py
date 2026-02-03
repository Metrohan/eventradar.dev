import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Any
from app.services.date_extractor import extract_date_from_text

def scrape_akbank_events() -> List[Dict[str, Any]]:
    # Selenium/UC imports are needed now
    import undetected_chromedriver as uc
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from app.scrapers.cs_scraper import get_chrome_options # Reuse options if possible or copy them

    url = "https://www.akbankgenclikakademisi.com/etkinlik-takvimi"
    base_url = "https://www.akbankgenclikakademisi.com"
    
    driver = None
    events = []
    
    try:
        # Use UC compatible options
        options = get_chrome_options()
        driver = uc.Chrome(options=options, use_subprocess=True, version_main=144)
        
        driver.get(url)
        
        # Wait for event items to be loaded
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.event-item"))
            )
        except Exception:
            print("Akbank: Timeout waiting for event items.")
            
        # Parse content with BS4 for easier traversal after loading
        soup = BeautifulSoup(driver.page_source, "html.parser")
        
        # Find active tab pane (usually 'Tümü' #nav-all)
        # The events are likely in #nav-all > #event-list-all
        container = soup.find('div', id='event-list-all')
        if container:
            cards = container.find_all('div', class_='event-item')
        else:
            cards = soup.find_all('div', class_='event-item')
            
        if cards:
            print("DEBUG Akbank First Card HTML:")
            print(cards[0].prettify())
            
        for card in cards:
            # Title
            title_tag = card.find('h6', class_='text-primary')
            title = title_tag.get_text(strip=True) if title_tag else 'Başlık yok'
            
            # Link
            link_tag = title_tag.find('a') if title_tag else None
            if link_tag and link_tag.has_attr('href'):
                href = link_tag['href']
                if href.startswith('http'):
                    url_ = href
                else:
                    url_ = base_url + ('/' + href if not href.startswith('/') else href)
            else:
                url_ = url
                
            # Image
            img_tag = card.find('a', class_='img-link')
            img = img_tag.find('img') if img_tag else None
            image_url = img['src'] if img and img.has_attr('src') else None
            if image_url and not image_url.startswith('http'):
                 image_url = base_url + image_url
            
            # Info extraction from div.info-list > div.d-flex
            # Structure: 
            # <div class="info-list ...">
            #   <div class="d-flex"> <span>Label</span> <span>:</span> <span>Value</span> </div>
            # </div>
            
            event_info_map = {}
            info_list = card.find('div', class_='info-list')
            if info_list:
                for row in info_list.find_all('div', class_='d-flex'):
                    spans = row.find_all('span')
                    if len(spans) >= 3:
                        label = spans[0].get_text(strip=True).replace(':', '')
                        value = spans[2].get_text(strip=True)
                        event_info_map[label] = value
            
            # Dates from Attributes (Reliable)
            # data-startdate="2027-01-01T00:00:00Z"
            raw_start_date = card.get('data-startdate')
            date_text = ''
            if raw_start_date:
                try:
                    dt = datetime.fromisoformat(raw_start_date.replace('Z', '+00:00'))
                    date_text = dt.strftime('%d.%m.%Y')
                except ValueError:
                     # Fallback to text
                     pass
            
            if not date_text:
                # Fallback to map
                date_text = event_info_map.get('Etkinlik Başlangıç', '')

            # Location from map
            location = event_info_map.get('Etkinlik Yeri', '')
            if not location:
                 # Check 'Etkinlik Formatı'
                 fmt = event_info_map.get('Etkinlik Formatı', '')
                 if fmt and fmt != '-':
                     location = fmt
            
            if not location or location == '-':
                 # Default
                 if any(city in title.lower() for city in ['izmir', 'istanbul', 'ankara', 'elazığ', 'adana']):
                     # Extract city from title if possible
                     for city in ['İzmir', 'İstanbul', 'Ankara', 'Elazığ', 'Adana']:
                         if city.lower() in title.lower():
                             location = city
                             break
                 else:
                     location = 'Online'

            # Description
            desc_text = f"Başvuru Bitiş: {card.get('data-applicationenddate')}"
            
            events.append({
                'title': title,
                'description': desc_text,
                'date': date_text,
                'location': location,
                'url': url_,
                'image_url': image_url,
                'source': 'Akbank Gençlik Akademisi',
                'is_active': True
            })
            
    except Exception as e:
        print(f"Akbank Scraper Error: {e}")
    finally:
        if driver:
            driver.quit()
            
    return events

if __name__ == "__main__":
    for e in scrape_akbank_events()[:3]:
        print(e)
