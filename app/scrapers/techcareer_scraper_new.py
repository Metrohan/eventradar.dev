"""
TechCareer.net Scraper - ChromeDriver düzeltmeli versiyon
"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import os
import glob
from datetime import datetime

def find_chromedriver():
    """ChromeDriver binary'yi bul"""
    # webdriver-manager cache dizinini kontrol et
    cache_dir = os.path.expanduser("~/.wdm/drivers/chromedriver")
    
    if os.path.exists(cache_dir):
        # En son sürümü bul
        versions = os.listdir(cache_dir)
        if versions:
            latest = sorted(versions)[-1]
            driver_dir = os.path.join(cache_dir, latest)
            
            # chromedriver binary'yi bul (THIRD_PARTY_NOTICES değil)
            for root, dirs, files in os.walk(driver_dir):
                for file in files:
                    if file == 'chromedriver' or file == 'chromedriver.exe':
                        driver_path = os.path.join(root, file)
                        # Executable olduğundan emin ol
                        os.chmod(driver_path, 0o755)
                        return driver_path
    
    return None

def scrape_techcareer_events():
    """TechCareer scraper - Düzeltilmiş ChromeDriver ile"""
    print("TechCareer.net etkinlikleri çekiliyor...")
    
    # ChromeDriver'ı bul
    driver_path = find_chromedriver()
    
    if not driver_path or not os.path.exists(driver_path):
        print(f"ChromeDriver bulunamadı veya geçersiz: {driver_path}")
        print("webdriver-manager ile indirme yapılıyor...")
        from webdriver_manager.chrome import ChromeDriverManager
        cache_path = ChromeDriverManager().install()
        driver_path = find_chromedriver()
        
        if not driver_path:
            print("ChromeDriver hala bulunamadı, atlanıyor")
            return []
    
    print(f"ChromeDriver bulundu: {driver_path}")
    
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    
    all_events = []
    driver = None
    
    try:
        service = Service(executable_path=driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        
        url = "https://www.techcareer.net/events"
        driver.get(url)
        
        # Sayfanın yüklenmesini bekle
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-test="single-event-box"]'))
        )
        time.sleep(3)
        
        # Sayfayı birkaç kez scroll et
        for _ in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        event_cards = soup.find_all(attrs={"data-test": "single-event-box"})
        
        print(f"TechCareer'den {len(event_cards)} etkinlik kartı bulundu")
        
        for card in event_cards:
            try:
                # Link
                link = card.get('href', '')
                if link and not link.startswith('http'):
                    link = f"https://www.techcareer.net{link}"
                
                # Başlık
                title_elem = card.find('h3', attrs={"data-test": "single-event-title"})
                title = title_elem.text.strip() if title_elem else "Başlık Bulunamadı"
                
                # Tarih
                date_elem = card.find('div', attrs={"data-test": "single-event-date"})
                date_str = date_elem.text.strip() if date_elem else None
                
                # Resim
                img_elem = card.find("img", attrs={"data-test": "single-event-image"})
                image_url = img_elem.get("src") if img_elem else None
                
                # Durum kontrolü
                open_btn = card.find('button', attrs={"data-test": "single-event-open-btn"})
                is_active = bool(open_btn)
                
                if is_active and link and title != "Başlık Bulunamadı":
                    all_events.append({
                        'title': title,
                        'description': "TechCareer.net etkinliği",
                        'date': date_str,
                        'location': "Online",
                        'url': link,
                        'image_url': image_url,
                        'source': "TechCareer.net",
                        'is_active': True
                    })
            except Exception as e:
                print(f"Etkinlik parse hatası: {e}")
                continue
        
        print(f"TechCareer'den {len(all_events)} aktif etkinlik çekildi")
        return all_events
        
    except Exception as e:
        print(f"TechCareer scraping hatası: {e}")
        import traceback
        traceback.print_exc()
        return []
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    events = scrape_techcareer_events()
    print(f"\nToplam {len(events)} etkinlik bulundu")
    for e in events[:3]:
        print(f"- {e['title']}")
