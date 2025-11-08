import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin
import re
import dateparser
try:
    from dateparser.search import search_dates  # optional, improves robustness
except Exception:  # pragma: no cover
    search_dates = None

def scrape_anbean_events():
    url = "https://anbeankampus.co/etkinlikler/"
    print(f"Anbean Kampüs etkinlikleri çekiliyor: {url}")

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36",
        "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8"
    }

    try:
        response = requests.get(url, timeout=20, headers=HEADERS)
        response.raise_for_status()
        response.encoding = 'utf-8'
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

        MONTHS_TR = {
            'Ocak': 1, 'Şubat': 2, 'Subat': 2, 'Mart': 3, 'Nisan': 4, 'Mayıs': 5, 'Mayis': 5,
            'Haziran': 6, 'Temmuz': 7, 'Ağustos': 8, 'Agustos': 8, 'Eylül': 9, 'Eylul': 9,
            'Ekim': 10, 'Kasım': 11, 'Kasim': 11, 'Aralık': 12, 'Aralik': 12
        }

        def parse_turkish_datetime(text: str):
            if not text:
                return None
            # Normalize separators like 16.00 -> 16:00 for better parsing
            norm = re.sub(r"(\d{1,2})\.(\d{2})(?!\d)", r"\1:\2", text)
            norm = norm.replace('Ã‡','Ç').replace('Ã¼','ü').replace('Ã–','Ö').replace('Ä°','İ').replace('Ã¶','ö').replace('ÃŸ','ß').replace('Ã§','ç').replace('ÄŸ','ğ').replace('Ã¶','ö').replace('ÅŸ','ş').replace('Ä±','ı')

            # Explicit month name pattern e.g. 12 Kasım 2025 16:00
            m = re.search(r"(\d{1,2})\s+(Ocak|Şubat|Subat|Mart|Nisan|Mayıs|Mayis|Haziran|Temmuz|Ağustos|Agustos|Eylül|Eylul|Ekim|Kasım|Kasim|Aralık|Aralik)\s+(\d{4})(?:\s+(\d{1,2})[:\.](\d{2}))?", norm, flags=re.IGNORECASE)
            if m:
                day = int(m.group(1))
                month_name = m.group(2)
                year = int(m.group(3))
                hour = int(m.group(4)) if m.group(4) else 0
                minute = int(m.group(5)) if m.group(5) else 0
                # Normalize key without accents fallback
                key_norm = month_name.capitalize()
                if key_norm not in MONTHS_TR:
                    # Try ascii version
                    key_norm = (key_norm
                                .replace('Ş','Subat') if key_norm=='Şubat' else key_norm
                                )
                month_num = MONTHS_TR.get(month_name, MONTHS_TR.get(key_norm))
                if month_num:
                    try:
                        return datetime(year, month_num, day, hour, minute)
                    except ValueError:
                        pass
            # Primary: use dateparser with Turkish
            dt = dateparser.parse(
                norm,
                languages=['tr'],
                settings={'DATE_ORDER': 'DMY', 'TIMEZONE': 'UTC', 'RETURN_AS_TIMEZONE_AWARE': False}
            )
            if dt:
                return dt
            # Fallback common numeric formats
            for fmt in ('%d.%m.%Y %H:%M', '%d/%m/%Y %H:%M', '%d.%m.%Y', '%d/%m/%Y'):
                try:
                    return datetime.strptime(norm, fmt)
                except ValueError:
                    continue
            return None

        event_date_obj = None
        if last_application_date_str != "Tarih Bulunamadı":
            event_date_obj = parse_turkish_datetime(last_application_date_str)

        # If time component missing or date not found, try detail page
        need_detail_lookup = (event_date_obj is None) or (event_date_obj and event_date_obj.hour == 0 and event_date_obj.minute == 0)
        # Debug omitted in production
        detail_date = None
        if need_detail_lookup and link:
            try:
                # Fetch detail page to get precise deadline with time
                detail_resp = requests.get(link, timeout=20, headers=HEADERS)
                detail_resp.raise_for_status()
                detail_resp.encoding = 'utf-8'
                detail_soup = BeautifulSoup(detail_resp.content, 'html.parser')

                # Primary selector: right wrapper spans (label + value)
                found_from_spans = False
                wrappers = detail_soup.select('.eventDetail-rs-ie-rightWrapper')
                for wrapper in wrappers:
                    spans = wrapper.find_all('span')
                    if len(spans) >= 2:
                        label = spans[0].get_text(strip=True)
                        value = spans[1].get_text(strip=True) if len(spans) > 1 else ''
                        if any(k in label for k in ["Son Kayıt", "Son Başvuru", "Son Kayıt Tarihi"]):
                            dd = parse_turkish_datetime(value)
                            if dd:
                                detail_date = dd
                                found_from_spans = True
                                break

                # Secondary: parse from <title>
                if not detail_date and detail_soup.title and detail_soup.title.string:
                    title_text = detail_soup.title.string.strip()
                    m = re.search(r"(\d{1,2}[\.\s]\w+\s\d{4}(?:\s\d{1,2}[:\.]\d{2})?)|(\d{1,2}[\./]\d{1,2}[\./]\d{4}(?:\s\d{1,2}[:\.]\d{2})?)", title_text)
                    if m:
                        dd = parse_turkish_datetime(m.group(0))
                        if dd:
                            detail_date = dd

                # Tertiary: search around label in full text
                if not detail_date:
                    detail_text = ' '.join(detail_soup.stripped_strings)
                    label_match = re.search(r"Son\s*(Kayıt|Başvuru)[^\d]{0,60}([\d\s:\.]+\w+\s+\d{4}(?:\s+[\d:\.]{4,5})?)", detail_text, flags=re.IGNORECASE)
                    if label_match:
                        captured = label_match.group(2) if label_match.lastindex and label_match.lastindex >= 2 else label_match.group(0)
                        detail_date = parse_turkish_datetime(captured)

                # Last resort: generic date search
                if not detail_date and search_dates:
                    dates_found = search_dates(' '.join(detail_soup.stripped_strings), languages=['tr']) or []
                    if dates_found:
                        detail_date = dates_found[0][1]

                if detail_date:
                    event_date_obj = detail_date
            except requests.exceptions.RequestException as de:
                print(f"Anbean detay sayfası alınamadı ({title}): {de}")

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