from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time 
from urllib.parse import urlparse, parse_qs, urljoin
from datetime import datetime
import requests
import tempfile

service = Service(ChromeDriverManager().install())
driver = None

def parse_techcareer_date(date_string):
    try:
        if '.' in date_string:
            return datetime.strptime(date_string, '%d.%m.%Y')
        elif '/' in date_string:
            return datetime.strptime(date_string, '%d/%m/%Y')
    except ValueError:
        return None
    return None

def scrape_techcareer_events():
    base_url = "https://www.techcareer.net"
    categories = {
        "Events": "/events"
    }

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

    all_events = []

    try:
        driver = webdriver.Chrome(service=service, options=options)

        for category_name, path in categories.items():
            url = f"{base_url}{path}"
            print(f"TechCareer.net {category_name} çekiliyor: {url}")
            driver.get(url)

            try:
                WebDriverWait(driver, 10).until( 
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-test="single-event-box"]'))
                )
                print(f"DEBUG: {category_name} - İlk etkinlik kartı bulundu.")
                time.sleep(5)
            except Exception as e:
                print(f"DEBUG: {category_name} sayfası için etkinlik kartları bulunamadı veya ilk yükleme başarısız oldu: {e}")
                continue 

            last_height = driver.execute_script("return document.body.scrollHeight")
            previous_event_count = 0
            no_new_content_count = 0
            max_no_new_content_attempts = 2

            initial_soup = BeautifulSoup(driver.page_source, 'html.parser')
            previous_event_count = len(initial_soup.find_all(attrs={"data-test": "single-event-box"}))
            print(f"DEBUG: {category_name} - Başlangıç etkinlik sayısı: {previous_event_count}, Sayfa Yüksekliği: {last_height}")


            while True:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                print(f"DEBUG: {category_name} - Sayfa aşağı kaydırıldı.")
                time.sleep(4)

                new_height = driver.execute_script("return document.body.scrollHeight")
                current_soup = BeautifulSoup(driver.page_source, 'html.parser')
                current_event_count = len(current_soup.find_all(attrs={"data-test": "single-event-box"}))
                
                print(f"DEBUG: {category_name} - Şu anki etkinlik sayısı: {current_event_count}, Yeni Sayfa Yüksekliği: {new_height}")

                if new_height == last_height and current_event_count == previous_event_count:
                    no_new_content_count += 1
                    print(f"DEBUG: {category_name} - İçerik veya yükseklik değişmedi. Deneme: {no_new_content_count}/{max_no_new_content_attempts}")
                    if no_new_content_count > max_no_new_content_attempts:
                        print(f"DEBUG: {category_name} sayfasında {max_no_new_content_attempts} ardışık kaydırma denemesinde yeni etkinlik/yükseklik bulunamadı, durduruluyor.")
                        break
                else:
                    no_new_content_count = 0

                last_height = new_height
                previous_event_count = current_event_count
                
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            event_cards = soup.find_all(attrs={"data-test": "single-event-box"})

            if not event_cards:
                print(f"DEBUG: {category_name} sayfasında 'data-test=\"single-event-box\"' niteliğine sahip etkinlik kartları bulunamadı.")
            else:
                print(f"DEBUG: {category_name} - Toplam bulunan etkinlik kartı sayısı (final): {len(event_cards)}")

            for card in event_cards:
                title = "Başlık Bulunamadı"
                link = None
                last_application_date_str = "Tarih Bulunamadı"
                is_active = False
                
                if 'href' in card.attrs:
                    link = card['href'].strip()
                    if not link.startswith('http'):
                        link = base_url + link

                title_element = card.find('h3', attrs={"data-test": "single-event-title"})
                if title_element:
                    title = title_element.text.strip()
                
                date_element = card.find('div', attrs={"data-test": "single-event-date"})
                if date_element:
                    last_application_date_str = date_element.text.strip()

                event_date_obj = parse_techcareer_date(last_application_date_str)

                description = f"{category_name} kategorisindeki TechCareer.net etkinliği."
                location = "Online"

                open_button = card.find('button', attrs={"data-test": "single-event-open-btn"})
                closed_button = card.find('button', attrs={"data-test": "single-event-closed-btn"})
                
                if open_button:
                    is_active = True
                elif closed_button:
                    is_active = False
                else:
                    is_active = False

                img_tag = card.find("img", attrs={"data-test": "single-event-image"})
                image_url = img_tag.get("src") if img_tag else None
                if image_url and not image_url.startswith("http"):
                    image_url = requests.compat.urljoin(url, image_url)

                if is_active and link and title != "Başlık Bulunamadı": 
                    all_events.append({
                        'title': title,
                        'description': description,
                        'date': event_date_obj,
                        'location': location,
                        'url': link,
                        "image_url": image_url,
                        'source': "TechCareer.net",
                        'is_active': is_active
                    })
                # else:
                #     print(f"TechCareer.net: Kapalı/Bilinmeyen ilan atlandı: {title} (Kategori: {category_name}, Durum: {status})")

    except Exception as e:
        print(f"TechCareer.net çekilirken genel bir hata oluştu: {e}")
        import traceback
        traceback.print_exc()
        if driver:
            driver.quit()
        raise
    finally:
        if driver:
            driver.quit()

    return all_events


if __name__ == "__main__":
    techcareer_events = scrape_techcareer_events()
    if techcareer_events:
        print("\n--- TechCareer.net Açık Etkinlikler ---")
        for event in techcareer_events:
            print(f"Başlık: {event.get('title')}")
            print(f"Açıklama: {event.get('description')}")
            print(f"Tarih: {event.get('date')}")
            print(f"Konum: {event.get('location')}")
            print(f"Resim: {event.get('image_url')}")
            print(f"URL: {event.get('url')}")
            print(f"Kaynak: {event.get('source')}")
            print(f"Aktif mi: {event.get('is_active')}")
            print("------------------------------------")
    else:
        print("TechCareer.net'te açık etkinlik bulunamadı veya çekilirken sorun oluştu.")