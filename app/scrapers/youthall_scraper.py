from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import os

def find_chromedriver():
    """ChromeDriver binary'yi bul"""
    cache_dir = os.path.expanduser("~/.wdm/drivers/chromedriver")
    if os.path.exists(cache_dir):
        versions = os.listdir(cache_dir)
        if versions:
            latest = sorted(versions)[-1]
            driver_dir = os.path.join(cache_dir, latest)
            for root, dirs, files in os.walk(driver_dir):
                for file in files:
                    if file == 'chromedriver':
                        driver_path = os.path.join(root, file)
                        os.chmod(driver_path, 0o755)
                        return driver_path
    return None

def scrape_youthall_events():
    """Youthall scraper"""
    driver_path = find_chromedriver()
    if not driver_path:
        from webdriver_manager.chrome import ChromeDriverManager
        try:
            ChromeDriverManager().install()
            driver_path = find_chromedriver()
        except Exception as e:
            print(f"Youthall: ChromeDriver yüklenemedi: {e}")
            return []
        if not driver_path:
            print("Youthall: ChromeDriver bulunamadı")
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
        
        # Sayfanın yüklenmesini bekle
        time.sleep(8)
        
        # Sayfa kaynağını al
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Etkinlik kartlarını bul - event-row class'ını kullan
        event_cards = soup.find_all('div', class_='event-row')
        
        events = []
        for card in event_cards:
            try:
                # Başlık - h3, h2 veya h4'ten al
                title_elem = card.find('h3') or card.find('h2') or card.find('h4')
                if not title_elem:
                    continue
                title = title_elem.text.strip()
                
                # Link - card içindeki ilk a tag
                link_elem = card.find('a', href=True)
                if not link_elem:
                    continue
                url = link_elem['href']
                if not url.startswith('http'):
                    url = 'https://www.youthall.com' + url
                
                # Tarih - events__content__datebox class'ından al
                date_elem = card.find('div', class_='events__content__datebox')
                date_str = date_elem.text.strip() if date_elem else None
                
                # Açıklama - events__content__details class'ından al
                desc_elem = card.find('div', class_='events__content__details')
                description = desc_elem.text.strip() if desc_elem else "Etkinlik açıklaması mevcut değil."
                
                # Görsel - img tag'inden al
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
                    'location': 'Online',  # Youthall genelde online etkinlikler
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
