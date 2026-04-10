from ssl import Options
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import tempfile
from urllib.parse import urljoin
from datetime import datetime
import shutil
import os
import dateparser

MAX_LOAD_ATTEMPTS = 2

service = Service(ChromeDriverManager().install())
driver = None

def parse_turkish_date(date_string):
    try:
        if not date_string:
            return None
        parsed = dateparser.parse(
            date_string.strip(),
            languages=['tr'],
            settings={
                'PREFER_DATES_FROM': 'future',
                'RELATIVE_BASE': datetime.now()
            }
        )
        return parsed
    except Exception:
        return None

def get_event_details(driver, event_url):
    event_start_date_str = "Başlangıç Tarihi Bulunamadı"
    event_end_date_str = "Bitiş Tarihi Bulunamadı"
    application_deadline_str = "Son Başvuru Tarihi Bulunamadı"
    location_str = "Konum Bulunamadı"
    description_str = "Açıklama Bulunamadı"

    try:
        driver.get(event_url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "c-job_detail_content_list"))
        )
        time.sleep(2)

        detail_soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        detail_list_items = detail_soup.find_all('div', class_='c-job_detail_content_list')

        for item in detail_list_items:
            feature_box = item.find('div', class_='c-job_detail_content_list_features')
            if feature_box:
                title_tag = feature_box.find('h6')
                date_tag = feature_box.find('small')
                
                if title_tag and date_tag:
                    title = title_tag.text.strip()
                    date_text = date_tag.text.strip()

                    if "Etkinlik Başlangıç" in title:
                        event_start_date_str = date_text
                    elif "Etkinlik Bitiş" in title:
                        event_end_date_str = date_text
                    elif "Son Başvuru" in title:
                        application_deadline_str = date_text
        
        description_div = detail_soup.find('div', class_='events_detail__content')
        if description_div:
            p_tag = description_div.find('p')
            if p_tag:
                description_str = p_tag.text.strip()
            elif description_div.text.strip():
                description_str = description_div.text.strip()
            else:
                description_str = "Etkinlik detay sayfasında açıklama bulunamadı."
        
        details_content = detail_soup.find('div', class_='events_detail__content')
        if details_content:
            location_element = details_content.find('span', string='Konum:')
            if location_element and location_element.find_next_sibling('span'):
                location_str = location_element.find_next_sibling('span').text.strip()
            elif "online" in detail_soup.get_text().lower():
                location_str = "Online"
            else:
                location_str = "Yerinde / Online Bilinmiyor"


    except Exception as e:
        print(f"Hata: Etkinlik detayları çekilirken sorun oluştu {event_url}: {e}")
    
    return event_start_date_str, event_end_date_str, application_deadline_str, location_str, description_str


def scrape_youthall_events():
    base_url = "https://www.youthall.com"
    events_url = "https://www.youthall.com/tr/events/" 

    print(f"\n--- Youthall Scraper Başlatılıyor ---")
    print(f"Youthall etkinlikleri çekiliyor: {events_url}")

    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    temp_profile = tempfile.mkdtemp()
    options.add_argument("--headless")             
    options.add_argument("--no-sandbox")           
    options.add_argument("--disable-dev-shm-usage")  
    options.add_argument("--disable-gpu")           
    options.add_argument("--window-size=1920,1080")  
    options.add_argument("--disable-extensions")    
    options.add_argument("--disable-infobars")
    options.add_argument(f"--user-data-dir={temp_profile}")
    driver = webdriver.Chrome(service=service, options=options)

    all_events = []
    current_date = datetime.now()

    try:
        driver.get(events_url)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "events"))
        )
        time.sleep(3) 

        current_attempts = 0
        while current_attempts < MAX_LOAD_ATTEMPTS:
            try:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                print(f"Youthall: Sayfa aşağı kaydırıldı (Deneme: {current_attempts + 1}/{MAX_LOAD_ATTEMPTS}).")
                time.sleep(3) 
                
                current_attempts += 1
            except Exception as e:
                print(f"Youthall: Daha fazla içerik yüklenemedi veya 'Daha Fazla' butonu bulunamadı. ({e})")
                break

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        event_cards = soup.select('div.events-card')

        if not event_cards:
            print("Hata: Youthall sayfasında etkinlik kartları bulunamadı (selector: .events-card).")
            return []

        for card in event_cards:
            title = "Başlık Bulunamadı"
            link = None
            image_url = None
            source = "Youthall"
            location = "Konum Bulunamadı"
            
            link_element = card.select_one('a.events-card__link[href]')
            if link_element and 'href' in link_element.attrs:
                link = urljoin(base_url, link_element['href'].strip())

            title_element = card.select_one('h2.events-card__title')
            if title_element:
                title = title_element.get_text(strip=True)

            company_element = card.select_one('div.events-card__company span')
            if company_element and company_element.get_text(strip=True):
                source = company_element.get_text(strip=True)

            location_element = card.select_one('div.events-card__location span')
            if location_element and location_element.get_text(strip=True):
                location = location_element.get_text(strip=True)

            image_element = card.select_one('div.events-card__img img')
            if image_element and image_element.get('src'):
                image_url = image_element.get('src').strip()

            description = f"Youthall etkinliği: {title}"

            # Yeni kart yapısından tarih alanlarını çek.
            event_start_date_str, event_end_date_str, application_deadline_str = "", "", ""
            for date_item in card.select('.events-card__dates .date-item'):
                label_element = date_item.select_one('.date-text small')
                value_element = date_item.select_one('.date-text strong')
                if not label_element or not value_element:
                    continue
                label = label_element.get_text(" ", strip=True).lower()
                value = value_element.get_text(" ", strip=True)
                if "son başvuru" in label or "son katılım" in label:
                    application_deadline_str = value
                elif "başlangıç" in label:
                    event_start_date_str = value
                elif "bitiş" in label:
                    event_end_date_str = value

            is_active = False
            final_event_date_for_db = None

            if application_deadline_str != "Son Başvuru Tarihi Bulunamadı" and application_deadline_str != "":
                deadline_date = parse_turkish_date(application_deadline_str)
                if deadline_date and deadline_date >= current_date.replace(hour=0, minute=0, second=0, microsecond=0): 
                    is_active = True
                    final_event_date_for_db = deadline_date
            
            
            if not is_active and event_start_date_str != "Başlangıç Tarihi Bulunamadı" and event_start_date_str != "":
                start_date = parse_turkish_date(event_start_date_str)
                end_date = parse_turkish_date(event_end_date_str) if event_end_date_str != "Bitiş Tarihi Bulunamadı" and event_end_date_str != "" else start_date
                
                if start_date and (start_date > current_date or (end_date and end_date >= current_date)):
                    is_active = True
                    final_event_date_for_db = start_date

            if is_active and title != "Başlık Bulunamadı" and link:
                all_events.append({
                    'title': title,
                    'description': description,
                    'date': final_event_date_for_db,
                    'location': location,
                    'image_url': image_url,
                    'url': link,
                    'source': source,
                    'is_active': True
                })
            else:
                print(f"Youthall: Geçmiş tarihli, başvuru süresi dolmuş veya eksik bilgiye sahip etkinlik atlandı: {title}")

        print(f"Youthall'dan {len(all_events)} aktif etkinlik başarıyla çekildi.")
        return all_events

    except Exception as e:
        print(f"Hata: Youthall scraper çalışırken bir sorun oluştu: {e}")
        import traceback
        traceback.print_exc() 
        return []
    finally:
        if driver:
            driver.quit()
        if temp_profile and os.path.isdir(temp_profile):
            shutil.rmtree(temp_profile, ignore_errors=True)

if __name__ == "__main__":
    open_events = scrape_youthall_events()
    if open_events:
        print("\n--- Youthall Aktif Etkinlikler ---")
        for event in open_events:
            print(f"Başlık: {event.get('title')}")
            print(f"Açıklama: {event.get('description')}")
            print(f"Tarih: {event.get('date')}")
            print(f"Konum: {event.get('location')}")
            print(f"URL: {event.get('url')}")
            print(f"Kaynak: {event.get('source')}")
            print(f"Aktif mi: {event.get('is_active')}")
            print("------------------------------------")
    else:
        print("Youthall'da aktif etkinlik bulunamadı.")
