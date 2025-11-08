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

def scrape_techcareer_events():
    """TechCareer scraper"""
    driver_path = find_chromedriver()
    if not driver_path:
        from webdriver_manager.chrome import ChromeDriverManager
        ChromeDriverManager().install()
        driver_path = find_chromedriver()
        if not driver_path:
            return []
    
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = None
    all_events = []
    
    try:
        driver = webdriver.Chrome(service=Service(driver_path), options=options)
        driver.get("https://www.techcareer.net/events")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-test="single-event-box"]')))
        time.sleep(3)
        
        for _ in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        for card in soup.find_all(attrs={"data-test": "single-event-box"}):
            try:
                link = card.get('href', '')
                if link and not link.startswith('http'):
                    link = f"https://www.techcareer.net{link}"
                
                title_elem = card.find('h3', attrs={"data-test": "single-event-title"})
                title = title_elem.text.strip() if title_elem else None
                
                date_elem = card.find('div', attrs={"data-test": "single-event-date"})
                date_str = date_elem.text.strip() if date_elem else None
                
                img_elem = card.find("img", attrs={"data-test": "single-event-image"})
                image_url = img_elem.get("src") if img_elem else None
                if image_url and not image_url.startswith('http'):
                    image_url = f"https://www.techcareer.net{image_url}"
                
                is_active = bool(card.find('button', attrs={"data-test": "single-event-open-btn"}))
                
                if is_active and link and title:
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
            except:
                continue
        return all_events
    except Exception as e:
        print(f"TechCareer hatası: {e}")
        return []
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    events = scrape_techcareer_events()
    print(f"Toplam {len(events)} etkinlik bulundu")
