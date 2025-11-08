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

def scrape_coderspace_events():
    """Coderspace scraper"""
    driver_path = find_chromedriver()
    if not driver_path:
        from webdriver_manager.chrome import ChromeDriverManager
        ChromeDriverManager().install()
        driver_path = find_chromedriver()
        if not driver_path:
            return []
    
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    service = Service(executable_path=driver_path)
    driver = None
    
    try:
        driver = webdriver.Chrome(service=service, options=options)
        
        # Cloudflare bypass için CDP komutları
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        })
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        driver.get('https://coderspace.io/etkinlikler')
        
        # Cloudflare challenge için daha uzun bekleme
        time.sleep(12)
        
        # Sayfa kaynağını al
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Cloudflare challenge sayfasında mıyız kontrol et
        if 'Verify you are human' in page_source or 'cloudflare' in page_source.lower():
            print("Coderspace: Cloudflare challenge aktif, etkinlik çekilemiyor")
            return []
        
        # Etkinlik kartlarını bul - farklı selector'lar dene
        event_cards = soup.find_all('div', class_='event-card')
        if not event_cards:
            event_cards = soup.find_all('div', class_='card')
        if not event_cards:
            event_cards = soup.find_all('article')
        
        # Eğer hiç kart bulunamazsa, tüm linkleri kontrol et
        if not event_cards:
            all_links = soup.find_all('a', href=lambda x: x and 'etkinlik' in str(x).lower())
            print(f"Coderspace: Kart bulunamadı, {len(all_links)} link kontrol ediliyor")
        
        events = []
        for card in event_cards:
            try:
                # Başlık
                title_elem = card.find('h3') or card.find('h2') or card.find('h4')
                if not title_elem:
                    continue
                title = title_elem.text.strip()
                
                # Link
                link_elem = card.find('a', href=True)
                if not link_elem:
                    continue
                url = link_elem['href']
                if not url.startswith('http'):
                    url = 'https://coderspace.io' + url
                
                # Tarih
                date_elem = card.find('span', class_='event-date') or card.find('time')
                date_str = date_elem.text.strip() if date_elem else None
                
                # Açıklama
                desc_elem = card.find('p', class_='event-description') or card.find('p')
                description = desc_elem.text.strip() if desc_elem else "Etkinlik açıklaması mevcut değil."
                
                # Görsel
                img_elem = card.find('img')
                image_url = img_elem.get('src', '') if img_elem else ''
                if image_url and not image_url.startswith('http'):
                    image_url = 'https://coderspace.io' + image_url
                
                events.append({
                    'title': title,
                    'url': url,
                    'date': date_str,
                    'description': description,
                    'image_url': image_url,
                    'source': 'Coderspace',
                    'location': 'Online',
                    'is_active': True
                })
                
            except Exception as e:
                print(f"Coderspace kart hatası: {e}")
                continue
        
        return events
        
    except Exception as e:
        print(f"Coderspace genel hatası: {e}")
        return []
        
    finally:
        if driver:
            driver.quit()
