import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin
from webdriver_manager.chrome import ChromeDriverManager

def scrape_anbean_events():
    url = "https://anbeankampus.co/etkinlikler/"
    print(f"Anbean Kampüs etkinlikleri çekiliyor: {url}")

    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"URL'ye erişilirken hata oluştu: {e}")
        return []
    
    soup = BeautifulSoup(response.content, 'html.parser')
    events = []

    event_cards = soup.find_all('div', class_='mini-eventCard')

    if not event_cards:
        print("Anbean Kampüs sayfasında etkinlik kartları bulunamadı. Selector'ı kontrol edin.")

    for card in event_cards:
        main_link_element = card.find('a', title=True)
        link = main_link_element['href'].strip() if main_link_element and 'href' in main_link_element.attrs else None
        if link and not link.startswith('http'):
            link = urljoin(url, link)

        title = main_link_element['title'].strip() if main_link_element and 'title' in main_link_element.attrs else "Başlık Bulunamadı"

        date_items = card.find('div', class_='mini-eventCard-dates')
        last_application_date_str = "Tarih Bulunamadı"
        if date_items:
            for item in date_items.find_all('div', class_='mini-eventCard-dateItem'):
                spans = item.find_all('span')
                if len(spans) == 2 and (spans[0].text.strip() == "Son Başvuru" or spans[0].text.strip() == "Son Kayıt"):
                    last_application_date_str = spans[1].text.strip()
                    break
        
        event_date_obj = None
        if last_application_date_str != "Tarih Bulunamadı":
            try:
                if '.' in last_application_date_str:
                    event_date_obj = datetime.strptime(last_application_date_str, '%d.%m.%Y')
                elif '/' in last_application_date_str:
                    event_date_obj = datetime.strptime(last_application_date_str, '%d/%m/%Y')
            except ValueError:
                print(f"Uyarı: Anbean etkinliği için tarih formatı tanınamadı: {last_application_date_str}")
                event_date_obj = None

        description = "Anbean Kampüs etkinliği."
        location = "Online"

        is_application_open = False
        status_closed_badge = card.find('span', class_='mini-eventCard-statusBadge text-danger')
        if status_closed_badge and "Başvurular Tamamlandı" in status_closed_badge.text:
            is_application_open = False
        else:
            detail_button = card.find('button', class_='btn-primary')
            if detail_button and "Detaylı Bilgi" in detail_button.text:
                is_application_open = True
        
        img_tag = card.find('img', class_='mini-eventCard-HeaderImage')
        if img_tag and 'src' in img_tag.attrs:
            image_url = img_tag['src']
            if not image_url.startswith('http'):
                image_url = urljoin(url, image_url)
        else:
            image_url = None
        
        if is_application_open and link and title != "Başlık Bulunamadı":
            events.append({
                'title': title,
                'description': description,
                'date': event_date_obj,
                'location': location,
                'url': link,
                'source': "Anbean",
                'is_active': True,
                'image_url': image_url
            })
        else:
            if title != "Başlık Bulunamadı":
                print(f"Anbean: Kapalı ilan atlandı veya gerekli bilgi eksik: {title}")
            else:
                print("Anbean: Bilgisi eksik veya kapalı bir etkinlik kartı atlandı.")
            pass

    return events

if __name__ == "__main__":
    open_events = scrape_anbean_events()
    if open_events:
        print("\n--- Anbean Kampüs Açık Etkinlikler ---")
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
        print("Anbean Kampüs'te açık etkinlik bulunamadı.")