from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re
import requests
import time

from .driver_utils import ensure_chromedriver
from ..services.date_extractor import parse_relative_turkish_datetime


def _fetch_event_details(detail_url: str) -> dict:
    """
    Etkinlik detay sayfasından gerçek tarih/saati ve açıklamayı çeker.

    Liste sayfasındaki "single-event-date" alanı aslında başvuru son tarihidir
    (bkz. "Son Başvuru: " etiketi); gerçek etkinlik tarihi/saati sadece detay
    sayfasındaki "Tarih:" satırında bulunur, örn: "19 Temmuz Pazar | 11.00 - 12.00".
    Açıklama ise "event-section-content-about" ("... Hakkında") bloğunda yer alır.
    """
    result: dict = {"date": None, "description": None}
    try:
        response = requests.get(detail_url, timeout=15)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        return result

    soup = BeautifulSoup(response.text, "html.parser")

    tarih_label = soup.find("strong", string=re.compile(r"^\s*Tarih:\s*$"))
    if tarih_label and tarih_label.parent:
        raw_text = tarih_label.parent.get_text(" ", strip=True)
        raw_text = raw_text.replace("Tarih:", "", 1).strip()
        result["date"] = parse_relative_turkish_datetime(raw_text)

    about_elem = soup.find(True, attrs={"data-test": "event-section-content-about"})
    if about_elem:
        description = about_elem.get_text("\n", strip=True)
        result["description"] = description or None

    return result


def scrape_techcareer_events():
    """TechCareer scraper"""
    driver_path = ensure_chromedriver()
    if not driver_path:
        print("TechCareer: ChromeDriver bulunamadı, atlanıyor")
        return []

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    driver = None
    all_events = []

    try:
        driver = webdriver.Chrome(service=Service(driver_path), options=options)
        driver.get("https://www.techcareer.net/events")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, '[data-test="single-event-box"]')
            )
        )
        time.sleep(3)

        for _ in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        for card in soup.find_all(attrs={"data-test": "single-event-box"}):
            try:
                link = card.get("href", "")
                if link and not link.startswith("http"):
                    link = f"https://www.techcareer.net{link}"

                title_elem = card.find("h3", attrs={"data-test": "single-event-title"})
                title = title_elem.text.strip() if title_elem else None

                # Bu alan aslında başvuru son tarihidir, etkinlik tarihi değil
                # (bkz. modülün başındaki _fetch_event_datetime docstring'i).
                deadline_elem = card.find(
                    "div", attrs={"data-test": "single-event-date"}
                )
                deadline_str = deadline_elem.text.strip() if deadline_elem else None

                img_elem = card.find("img", attrs={"data-test": "single-event-image"})
                image_url = img_elem.get("src") if img_elem else None
                if image_url and not image_url.startswith("http"):
                    image_url = f"https://www.techcareer.net{image_url}"

                is_active = bool(
                    card.find("button", attrs={"data-test": "single-event-open-btn"})
                )

                if is_active and link and title:
                    details = _fetch_event_details(link)
                    all_events.append(
                        {
                            "title": title,
                            "description": details["description"]
                            or "TechCareer.net etkinliği",
                            "date": details["date"],
                            "application_deadline": deadline_str,
                            "location": "Online",
                            "url": link,
                            "image_url": image_url,
                            "source": "TechCareer.net",
                            "is_active": True,
                        }
                    )
            except Exception:
                continue
        return all_events
    except Exception as e:
        print(f"TechCareer hatası: {e}")
        return []
    finally:
        if driver:
            driver.quit()


if __name__ == "__main__":
    events = scrape_techcareer_events()
    print(f"Toplam {len(events)} etkinlik bulundu")
