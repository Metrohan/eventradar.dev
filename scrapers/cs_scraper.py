from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin
from datetime import datetime
import tempfile



def parse_coderspace_date(date_string):
    months_turkish = {
        'Ocak': 1, 'Şubat': 2, 'Mart': 3, 'Nisan': 4, 'Mayıs': 5, 'Haziran': 6,
        'Temmuz': 7, 'Ağustos': 8, 'Eylül': 9, 'Ekim': 10, 'Kasım': 11, 'Aralık': 12
    }
    try:
        parts = date_string.split()
        if len(parts) < 3:
            print(f"Tarih formatı beklenmedik: {date_string}")
            return None
        day = int(parts[0])
        month = months_turkish.get(parts[1])
        year = int(parts[2])
        if month:
            return datetime(year, month, day)
        else:
            print(f"Geçersiz ay ismi: {parts[1]} - Tarih: {date_string}")
            return None
    except (ValueError, KeyError) as e:
        print(f"Tarih parse hatası: {date_string} - Hata: {e}")
        return None

def scrape_coderspace_events():
    url = "https://coderspace.io/etkinlikler"
    print(f"Coderspace etkinlikleri çekiliyor: {url}")

    options = Options()
    options.add_argument("--headless")             
    options.add_argument("--no-sandbox")           
    options.add_argument("--disable-dev-shm-usage")  
    options.add_argument("--disable-gpu")           
    options.add_argument("--window-size=1920,1080")  
    options.add_argument("--disable-extensions")    
    options.add_argument("--disable-infobars")
    options.add_argument(f"--user-data-dir={tempfile.mkdtemp()}")

    service = Service(ChromeDriverManager().install())
    driver = None

    events = []

    try:
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)

        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.events-live-list div.col-12'))
        )
        time.sleep(3)

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        event_cards = soup.find_all('div', class_='col-12 col-lg-6 col-xl-4')

        if not event_cards:
            print("Coderspace sayfasında etkinlik kartları (col-12 div'leri) bulunamadı.")
            return []

        for card_col_div in event_cards:
            card = card_col_div.find('div', class_='event-card')
            if not card:
                continue

            title_link_element = card.find('h5', class_='mt-3')
            if title_link_element:
                title_link_element = title_link_element.find('a')

            title = title_link_element.text.strip() if title_link_element else "Başlık Bulunamadı"
            link = title_link_element['href'].strip() if title_link_element and 'href' in title_link_element.attrs else None
            
            if link and not link.startswith('http'):
                link = urljoin(url, link)

            img_tag = card.find('div', class_='event-card-image').find('img')
            image_url = img_tag['src'] if img_tag and 'src' in img_tag.attrs else None
            if image_url and not image_url.startswith('http'):
                image_url = urljoin(url, image_url)

            last_application_date_str = "Tarih Bulunamadı"
            info_list = card.find('ul', class_='event-card-info')
            if info_list:
                for item in info_list.find_all('li'):
                    spans = item.find_all('span')
                    strong_tag = item.find('strong')
                    if len(spans) > 0 and spans[0].text.strip() == "Son Başvuru" and strong_tag:
                        last_application_date_str = strong_tag.text.strip()
                        break
            
            event_date_obj = parse_coderspace_date(last_application_date_str)
            
            category_element = card.find('span', class_='event-card-type')
            category = category_element.text.strip() if category_element else "Kategori Bulunamadı"

            is_application_open = False 
            main_button = card.find('a', class_='primary-button--big')
            
            if main_button:
                if 'primary-button--disabled' in main_button.get('class', []):
                    is_application_open = False
                else:
                    is_application_open = True
            
            description = f"{category} kategorisindeki Coderspace etkinliği."
            location = "Online"
            if is_application_open and link and title != "Başlık Bulunamadı":
                events.append({
                    'title': title,
                    'description': description,
                    'date': event_date_obj,
                    'location': location,
                    'url': link,
                    'source': "Coderspace",
                    'is_active': is_application_open,
                    'image_url': image_url
                })
            # else:
            #     print(f"Coderspace: Kapalı/Bilinmeyen ilan atlandı: {title}")

    except Exception as e:
        print(f"Coderspace çekilirken hata oluştu: {e}")
        import traceback
        traceback.print_exc()
        if driver:
            driver.quit()
        raise
    finally:
        if driver:
            driver.quit()

    return events

if __name__ == "__main__":
    coderspace_events = scrape_coderspace_events()
    if coderspace_events:
        print("\n--- Coderspace Açık Etkinlikler ---")
        for event in coderspace_events:
            print(f"Başlık: {event.get('title')}")
            print(f"Açıklama: {event.get('description')}")
            print(f"Tarih: {event.get('date')}")
            print(f"Konum: {event.get('location')}")
            print(f"URL: {event.get('url')}")
            print(f"Resim: {event.get['image_url']}")
            print(f"Kaynak: {event.get('source')}")
            print(f"Aktif mi: {event.get('is_active')}")
            print("------------------------------------")
    else:
        print("Coderspace'te açık etkinlik bulunamadı veya çekilirken sorun oluştu.")