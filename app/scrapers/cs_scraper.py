import logging
import time
from datetime import datetime
from typing import List, Dict, Any, Optional

from bs4 import BeautifulSoup, Tag
import undetected_chromedriver as uc

logger = logging.getLogger(__name__)

_MONTH_TR = {
    "ocak": 1,
    "subat": 2,
    "mart": 3,
    "nisan": 4,
    "mayis": 5,
    "haziran": 6,
    "temmuz": 7,
    "agustos": 8,
    "eylul": 9,
    "ekim": 10,
    "kasim": 11,
    "aralik": 12,
    "şubat": 2,
    "mayıs": 5,
    "ağustos": 8,
    "eylül": 9,
    "kasım": 11,
    "aralık": 12,
}


def _parse_tr_date(date_str: str, prefer_future: bool = False) -> Optional[datetime]:
    """
    '12 Temmuz' veya '12 Temmuz 2026' gibi Türkçe tarihi parse eder.
    prefer_future=True: yil yoksa ve tarih gecmisteyse bir sonraki yila atar.
    prefer_future=False: yil yoksa her zaman mevcut yili kullanir (deadline filtresi icin).
    """
    if not date_str:
        return None
    parts = date_str.strip().lower().split()
    if len(parts) < 2:
        return None
    try:
        day = int(parts[0])
        month = _MONTH_TR.get(parts[1])
        if not month:
            return None
        year = int(parts[2]) if len(parts) >= 3 else datetime.now().year
        dt = datetime(year, month, day)
        if prefer_future and len(parts) < 3 and dt < datetime.now():
            dt = dt.replace(year=dt.year + 1)
        return dt
    except (ValueError, TypeError):
        return None


def get_chrome_options() -> uc.ChromeOptions:
    options = uc.ChromeOptions()
    options.add_argument("--headless=old")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--blink-settings=imagesEnabled=false")
    return options


def scrape_coderspace_events() -> List[Dict[str, Any]]:
    driver = None
    events = []
    now = datetime.now()

    try:
        from app.scrapers.driver_utils import create_uc_driver

        driver = create_uc_driver(options=get_chrome_options())

        driver.get("https://coderspace.io/etkinlikler")
        time.sleep(6)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        cards = soup.select("div.event-card")
        logger.info(f"Coderspace: {len(cards)} kart bulundu")

        skipped = 0
        for card in cards:
            try:
                link_elem = card.select_one(".event-card-image a")
                href = str(link_elem.get("href", "")) if link_elem else ""
                if not href or "/etkinlikler/" not in href or "/pro/" in href:
                    continue

                url = (
                    href if href.startswith("http") else f"https://coderspace.io{href}"
                )

                title_elem = card.select_one("h5.mt-3 a") or card.select_one("h5 a")
                if title_elem:
                    title = title_elem.get_text(strip=True)
                else:
                    img = link_elem.find("img") if link_elem else None
                    title = (
                        str(img.get("alt", "")).strip() if isinstance(img, Tag) else ""
                    )
                if not title:
                    continue

                date_map: Dict[str, str] = {}
                for li in card.select("ul.event-card-info li"):
                    span = li.find("span")
                    strong = li.find("strong")
                    if span and strong:
                        date_map[span.get_text(strip=True)] = strong.get_text(
                            strip=True
                        )

                # Filtreleme: prefer_future=False — yil rollover yapma, mevcut yili kullan.
                # Gecmis yildaki "Aralik" gibi durumlar da dogru sekilde gecmis sayilir.
                deadline_str = date_map.get("Son Başvuru") or date_map.get("Bitiş")
                if deadline_str:
                    deadline_dt = _parse_tr_date(deadline_str, prefer_future=False)
                    if deadline_dt and deadline_dt < now:
                        skipped += 1
                        continue

                # DB icin en anlamli tarih: Bitis > Baslangic > Son Basvuru
                # prefer_future=True: gelecekteki Aralik/Ocak etkinlikleri icin dogru yili tahmin et
                date_val = None
                for label in ("Bitiş", "Başlangıç", "Son Başvuru"):
                    if label in date_map:
                        date_val = _parse_tr_date(date_map[label], prefer_future=True)
                        if date_val:
                            break

                date_str_out = date_val.strftime("%-d %B %Y") if date_val else None

                desc_elem = card.select_one("p")
                description = desc_elem.get_text(strip=True) if desc_elem else ""

                event_type_elem = card.select_one(".event-card-type")
                event_type = (
                    event_type_elem.get_text(strip=True) if event_type_elem else ""
                )

                img_elem = card.select_one(".event-card-image img")
                image_url = ""
                if img_elem:
                    src = str(img_elem.get("src", ""))
                    image_url = (
                        src if src.startswith("http") else f"https://coderspace.io{src}"
                    )

                events.append(
                    {
                        "title": title,
                        "url": url,
                        "date": date_str_out,
                        "description": description
                        or f"Coderspace {event_type} etkinligi.",
                        "image_url": image_url,
                        "source": "Coderspace",
                        "location": "Online",
                        "is_active": True,
                    }
                )

            except Exception as e:
                logger.error(f"Coderspace kart hatasi: {e}", exc_info=False)
                continue

        logger.info(
            f"Coderspace: {skipped} gecmis etkinlik atlandi, {len(events)} aktif kaldi"
        )
        return events

    except Exception as e:
        logger.error(f"Coderspace genel hata: {e}", exc_info=True)
        return []

    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass
