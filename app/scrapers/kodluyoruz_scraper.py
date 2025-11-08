import requests
from bs4 import BeautifulSoup

BASE_URL = "https://kodluyoruz.org"
URL = f"{BASE_URL}/programlar"  # Kodluyoruz etkinlik sayfası

def scrape_kodluyoruz_events():
    response = requests.get(URL)
    response.raise_for_status()
    response.encoding = 'utf-8'
    
    soup = BeautifulSoup(response.text, "html.parser")

    programlar = []
    
    for program in soup.select(".single-program-wrapper"):
        try:
            # Başlık
            title_tag = program.select_one(".program-ad")
            title = title_tag.get_text(strip=True) if title_tag else None
            
            # Görsel
            img_tag = program.select_one(".program-img")
            image = img_tag["src"] if img_tag else None
            
            # Tarihler
            tarih_elements = program.select(".program-detail-tarih")
            son_basvuru = tarih_elements[0].get_text(strip=True) if len(tarih_elements) > 0 else None
            baslangic = tarih_elements[1].get_text(strip=True) if len(tarih_elements) > 1 else None
            
            # Link
            link_tag = program.select_one(".program-btn.w-button")
            link = f"{BASE_URL}{link_tag['href']}" if link_tag and 'href' in link_tag.attrs else None
            
            # Format (Ücretsiz vs.)
            format_tag = program.select_one(".program-format")
            format_text = format_tag.get_text(strip=True) if format_tag else None

            # Standart format
            programlar.append({
                "title": title,
                "description": format_text,
                "date": baslangic,  # Başlangıç tarihini kullan
                "location": None,
                "url": link,
                "source": "Kodluyoruz",
                "is_active": True,
                "image_url": image
            })
        except Exception as e:
            print(f"Hata: {e}")

    return programlar

if __name__ == "__main__":
    data = scrape_kodluyoruz_events()
    for e in data:
        print(e)
