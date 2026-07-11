import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Any
from app.services.date_extractor import extract_date_from_text


def _build_description(title: str, egitmenler: str, application_deadline: str) -> str:
    """
    Pupilica'nın etkinlik kartlarında/detay sayfasında gerçek bir açıklama metni
    bulunmuyor (site tamamen istemci tarafında render ediliyor ve bot korumalı
    olduğu için detay sayfası da güvenilir şekilde çekilemiyor). Elimizdeki
    alanlardan (başlık, eğitmen, son başvuru) okunaklı bir Türkçe cümle üretiyoruz.
    """
    parts = [f"{title} etkinliği Pupilica üzerinde düzenleniyor."]
    if egitmenler:
        parts.append(f"Eğitmen: {egitmenler}.")
    if application_deadline:
        parts.append(f"Son başvuru: {application_deadline}.")
    return " ".join(parts)


def scrape_pupilica_events() -> List[Dict[str, Any]]:
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from app.scrapers.cs_scraper import get_chrome_options
    from app.scrapers.driver_utils import create_uc_driver

    url = "https://pupilica.com/events"
    base_url = "https://pupilica.com"

    driver = None
    events = []

    try:
        # Initializing undetected-chromedriver
        options = get_chrome_options()
        driver = create_uc_driver(options=options)

        driver.get(url)

        # Wait for event cards (partial class match)
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div[class*='EventsCard__CardWrapper']")
                )
            )
        except Exception:
            print("Pupilica: Timeout waiting for event cards.")

        # Parse rendered content
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Select cards using partial class match
        cards = soup.select("div[class*='EventsCard__CardWrapper']")

        for card in cards:
            # Image
            img_tag = card.find("img")
            image_url = img_tag["src"] if img_tag and img_tag.has_attr("src") else None

            # Title
            # Look for h3 inside the card
            title_tag = card.find("h3")
            title = title_tag.get_text(strip=True) if title_tag else "Başlık yok"

            # Info rows
            # Traverse divs looking for spans with labels
            date_text = ""
            application_deadline = ""
            egitmenler = ""

            # Get all text content to parse if specific classes invalid
            # Or traverse children
            rows = card.find_all("div", recursive=False)
            # Recursively find rows that contain spans

            # Let's try to find spans with specific text
            all_spans = card.find_all("span")
            for i, span in enumerate(all_spans):
                text = span.get_text(strip=True)
                if "Tarih" in text and i + 1 < len(all_spans):
                    date_text = all_spans[i + 1].get_text(strip=True)
                elif "Son Başvuru" in text and i + 1 < len(all_spans):
                    application_deadline = all_spans[i + 1].get_text(strip=True)
                elif "Eğitmen" in text and i + 1 < len(all_spans):
                    egitmenler = all_spans[i + 1].get_text(strip=True)

            # Description: gerçek açıklama metni sitede bulunmuyor (bkz.
            # _build_description docstring'i), okunaklı bir cümle üretiyoruz.
            desc_text = _build_description(title, egitmenler, application_deadline)

            # Link
            # Try to find a link (a tag) inside the card or parent
            a_tag = card.find("a", href=True)
            if not a_tag:
                # Check parent
                parent = card.find_parent("a", href=True)
                if parent:
                    a_tag = parent

            if a_tag:
                url_ = base_url + str(a_tag["href"])
            else:
                import re

                # Generate a unique slug from title if no link is found
                slug = re.sub(r"[\W_]+", "-", title.lower()).strip("-")
                url_ = f"{url}#{slug}"

            # Location
            # Pupilica events are mostly online, but we can check if text says otherwise
            location = "Online"

            events.append(
                {
                    "title": title,
                    "description": desc_text,
                    "date": date_text,
                    "application_deadline": application_deadline,
                    "location": location,
                    "url": url_,
                    "image_url": image_url,
                    "source": "Pupilica",
                    "is_active": True,
                }
            )

    except Exception as e:
        print(f"Pupilica Scraper Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        if driver:
            driver.quit()

    return events


if __name__ == "__main__":
    for e in scrape_pupilica_events()[:3]:
        print(e)
