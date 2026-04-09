from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime
import tempfile
MAX_LOAD_ATTEMPTS = 0

service = Service(ChromeDriverManager().install())
driver = None

def parse_kodluyoruz_date(date_string):
    try:
        if '.' in date_string:
            return datetime.strptime(date_string, '%d.%m.%Y')
        elif '/' in date_string:
            return datetime.strptime(date_string, '%d/%m/%Y')
    except ValueError:
        return None
    return None

def scrape_kodluyoruz_events():

    url = "https://www.kodluyoruz.org/programlar"
    base_url = "https://www.kodluyoruz.org"

    print(f"\n--- Kodluyoruz Scraper Başlatılıyor ---")
    print(f"Kodluyoruz etkinlikleri çekiliyor: {url}")

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")             
    options.add_argument("--no-sandbox")           
    options.add_argument("--disable-dev-shm-usage")  
    options.add_argument("--disable-gpu")           
    options.add_argument("--window-size=1920,1080")  
    options.add_argument("--disable-extensions")    
    options.add_argument("--disable-infobars")
    options.add_argument(f"--user-data-dir={tempfile.mkdtemp()}")

    try:
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "all-programs-tabs"))
        )
        time.sleep(2)

        try:
            target_tab_xpath = "//a[contains(@class, 'all-programs-tabs')]//div[contains(@class, 'all-program-tap-text') and contains(text(), 'Genç & Genç Yetişkinler İçin')]"
            
            target_tab_div = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, target_tab_xpath))
            )
            driver.execute_script("arguments[0].click();", target_tab_div.find_element(By.XPATH, ".."))
            print("✔ 'Genç & Genç Yetişkinler İçin' sekmesine tıklandı.")
            time.sleep(3)

        except Exception as e:
            print(f"Uyarı: 'Genç & Genç Yetişkinler İçin' sekmesine tıklanırken sorun oluştu: {e}")
            print("Sayfa varsayılan sekmede taranmaya devam edecek.")

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        events = []

        event_cards = soup.find_all('div', class_='program-erik-wrap')

        if not event_cards:
            print("Hata: Kodluyoruz sayfasında 'program-erik-wrap' sınıfına sahip etkinlik kartları bulunamadı.")
            print("Lütfen selector'ı veya sayfa yüklenme durumunu kontrol edin.")
            return []

        for card in event_cards:
            title = "Başlık Bulunamadı"
            link = None
            last_application_date_str = "Tarih Bulunamadı"
            category = "Kategori Bulunamadı"
            is_active = False

            title_element = card.find('h5', class_='program-ad programlar')
            if title_element:
                title = title_element.text.strip()

            link_element = card.find('a', class_='program-btn')
            if link_element and 'href' in link_element.attrs:
                link = urljoin(base_url, link_element['href'].strip())

            img_element = card.find('img', class_='program-img')
            program_img = img_element['src'] if img_element and 'src' in img_element.attrs else None

            date_flex_divs = card.find_all('div', class_='program-detay-flex')
            for div in date_flex_divs:
                detail_label = div.find('div', class_='program-detail')
                detail_value = div.find('div', class_='program-detail-tarih')
                if detail_label and detail_value and "Son Başvuru Tarihi:" in detail_label.text:
                    last_application_date_str = detail_value.text.strip()
                    break
            
            event_date_obj = parse_kodluyoruz_date(last_application_date_str)

            format_category_element = card.find('div', class_='program-format')
            if format_category_element:
                category = format_category_element.text.strip()
            else:
                category = "Program"

            active_apply_button = None
            apply_buttons = card.find_all('a', class_='program-btn', text="Şimdi Başvur")
            for btn in apply_buttons:
                if 'w-condition-invisible' not in btn.get('class', []):
                    active_apply_button = btn
                    break

            if active_apply_button:
                is_active = True
            else:
                is_active = False

            description = f"{category} kategorisindeki Kodluyoruz programı."
            location = "Online"

            if is_active and link and title != "Başlık Bulunamadı":
                events.append({
                    'title': title,
                    'description': description,
                    'date': event_date_obj,
                    'location': location,
                    'image_url': program_img,  
                    'url': link,
                    'source': "Kodluyoruz",
                    'is_active': is_active
                })
            # else:
            #     print(f"Kodluyoruz: Kapalı ilan atlandı: {title}")

        print(f"Kodluyoruz'dan {len(events)} açık etkinlik başarıyla çekildi.")
        return events

    except Exception as e:
        print(f"Hata: Kodluyoruz scraper çalışırken bir sorun oluştu: {e}")
        import traceback
        traceback.print_exc()
        if driver:
            driver.quit()
        raise
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    open_events = scrape_kodluyoruz_events()
    if open_events:
        print("\n--- Kodluyoruz Açık Etkinlikler ---")
        for event in open_events:
            print(f"Başlık: {event.get('title')}")
            print(f"Açıklama: {event.get('description')}")
            print(f"Tarih: {event.get('date')}")
            print(f"Konum: {event.get('location')}")
            print(f"Resim URL: {event.get('image_url')}")
            print(f"URL: {event.get('url')}")
            print(f"Kaynak: {event.get('source')}")
            print(f"Aktif mi: {event.get('is_active')}")
            print("------------------------------------")
    else:
        print("Kodluyoruz'da açık etkinlik bulunamadı.")