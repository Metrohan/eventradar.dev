import requests
from bs4 import BeautifulSoup

API_URL = "https://api.ibb.gov.tr/techistanbul-backend/api/events"
UPLOADS_BASE = "https://api.ibb.gov.tr/techistanbul-backend/uploads"
DETAIL_BASE = "https://tech.istanbul/etkinlikler"

# Tech Istanbul, konum bilgisini slug halinde döner (örn. "kucukcekmece");
# kartlarda göstermek için Türkçe karşılıklarına çeviriyoruz.
LOCATION_NAMES = {
    "kucukcekmece": "Küçükçekmece",
    "kayisdagi": "Kayışdağı",
    "sisli": "Şişli",
    "sishane": "Şişhane",
    "miniaturk": "Miniatürk",
    "online": "Online",
}


def _clean_description(html: str) -> str:
    """Zengin HTML açıklamayı, EventDetailPage'in beklediği düz metne çevirir."""
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text("\n", strip=True)


def scrape_techistanbul_events():
    """
    Tech Istanbul (İBB girişimcilik merkezi) etkinlikleri.

    Site tamamen istemci tarafında render edilen bir SPA, ama arkasında
    doğrudan çekilebilen açık bir JSON API var — Selenium'a gerek yok.
    """
    try:
        response = requests.get(API_URL, timeout=20, params={"page": 1, "limit": 100})
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Tech Istanbul: network error: {e}")
        return []

    try:
        payload = response.json()
    except ValueError:
        print("Tech Istanbul: geçersiz JSON yanıtı")
        return []

    if not payload.get("isSuccess"):
        print("Tech Istanbul: API isSuccess=false döndü")
        return []

    events = []
    for item in payload.get("data", []):
        try:
            if not item.get("isActive"):
                continue

            title = item.get("title")
            slug = item.get("slug")
            if not title or not slug:
                continue

            schedules = item.get("schedules") or []
            date = schedules[0].get("startTime") if schedules else None

            is_online = bool(item.get("isOnline"))
            location_slug = item.get("locationName")
            location = (
                "Online"
                if is_online
                else LOCATION_NAMES.get(
                    location_slug, (location_slug or "").capitalize() or None
                )
            )

            file_path = item.get("filePath")
            image_url = f"{UPLOADS_BASE}/{file_path}" if file_path else None

            events.append(
                {
                    "title": title,
                    "description": _clean_description(item.get("description", "")),
                    "date": date,
                    "application_deadline": item.get("applicationEnd"),
                    "location": location,
                    "url": f"{DETAIL_BASE}/{slug}",
                    "image_url": image_url,
                    "source": "Tech Istanbul",
                    "is_active": True,
                }
            )
        except Exception as e:
            print(f"Tech Istanbul: etkinlik işlenirken hata: {e}")
            continue

    return events


if __name__ == "__main__":
    for e in scrape_techistanbul_events()[:3]:
        print(e)
