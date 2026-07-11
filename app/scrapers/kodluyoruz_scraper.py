import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any

BASE_URL = "https://kodluyoruz.org"
URL = f"{BASE_URL}/programlar"  # Kodluyoruz etkinlik sayfası


def _fetch_program_description(detail_url: str) -> str | None:
    """Program detay sayfasındaki gerçek açıklamayı çeker (liste sayfasındaki
    '.program-format' alanı sadece 'Ücretsiz' gibi bir etikettir, açıklama değil)."""
    try:
        response = requests.get(detail_url, timeout=15)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    desc_elem = soup.select_one("p.single-course-details")
    if not desc_elem:
        return None
    return desc_elem.get_text(" ", strip=True) or None


def scrape_kodluyoruz_events() -> List[Dict[str, Any]]:
    """Scrape active programs/events from Kodluyoruz.

    Returns a list of dicts, one per program, with the following keys:

    - ``title`` (str): Program name (e.g. "Python ile Veri Bilimi")
    - ``description`` (str): Real description fetched from the program's
      detail page, falling back to the format label (e.g. "Ücretsiz") if
      the detail page has none
    - ``date`` (str | None): Program start date (``başlangıç``)
    - ``application_deadline`` (str | None): Application deadline (``son
      başvuru``)
    - ``location`` (None): Not available from this page
    - ``url`` (str | None): Absolute URL to the program detail page
    - ``source`` (str): Always ``"Kodluyoruz"``
    - ``is_active`` (bool): Always ``True``
    - ``image_url`` (str | None): URL of the program thumbnail image
    """
    try:
        response = requests.get(URL, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Kodluyoruz: network error: {e}")
        return []
    response.encoding = "utf-8"

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
            son_basvuru = (
                tarih_elements[0].get_text(strip=True)
                if len(tarih_elements) > 0
                else None
            )
            baslangic = (
                tarih_elements[1].get_text(strip=True)
                if len(tarih_elements) > 1
                else None
            )

            # Link
            link_tag = program.select_one(".program-btn.w-button")
            link = (
                f"{BASE_URL}{link_tag['href']}"
                if link_tag and "href" in link_tag.attrs
                else None
            )

            # Format (Ücretsiz vs.)
            format_tag = program.select_one(".program-format")
            format_text = format_tag.get_text(strip=True) if format_tag else None

            description = (_fetch_program_description(link) if link else None) or format_text

            # Standart format
            programlar.append(
                {
                    "title": title,
                    "description": description,
                    "date": baslangic,  # Başlangıç tarihini kullan
                    "application_deadline": son_basvuru,
                    "location": None,
                    "url": link,
                    "source": "Kodluyoruz",
                    "is_active": True,
                    "image_url": image,
                }
            )
        except Exception as e:
            print(f"Hata: {e}")

    return programlar


if __name__ == "__main__":
    data = scrape_kodluyoruz_events()
    for e in data:
        print(e)
