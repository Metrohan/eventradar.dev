import logging
import time
from typing import List, Dict, Any, Optional

from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configure module-level logger
logger = logging.getLogger(__name__)


def get_chrome_options() -> uc.ChromeOptions:
    """Configures optimized Chrome options for headless execution with UC."""
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    # Block unnecessary resources to save bandwidth/memory
    options.add_argument("--blink-settings=imagesEnabled=false")

    return options


def scrape_coderspace_events() -> List[Dict[str, Any]]:
    """
    Optimized Coderspace scraper using undetected-chromedriver to bypass Cloudflare.
    """
    driver = None
    events = []

    try:
        # Initializing undetected-chromedriver
        # Specify version_main to match installed Chrome 144
        driver = uc.Chrome(
            options=get_chrome_options(), use_subprocess=True, version_main=144
        )

        url = "https://coderspace.io/etkinlikler"
        driver.get(url)

        # Cloudflare Bypass Strategy: Check for iframe and click
        try:
            # Wait a bit for initial load
            time.sleep(3)

            # Check for Cloudflare challenge iframe
            cf_frames = driver.find_elements(
                By.XPATH,
                "//iframe[contains(@src, 'cloudflare') or contains(@title, 'Widget containing a Cloudflare security challenge')]",
            )

            if cf_frames:
                logger.info(
                    "Coderspace: Cloudflare challenge found. Attempting to click..."
                )
                driver.switch_to.frame(cf_frames[0])

                # Try to find the checkbox/button
                # Usually it's a checkbox or a div inside the iframe
                checkbox = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            "//label[@class='ctp-checkbox-label'] | //div[@class='ctp-checkbox-container'] | //input[@type='checkbox']",
                        )
                    )
                )

                if checkbox:
                    checkbox.click()
                    logger.info("Coderspace: Clicked Cloudflare checkbox.")

                # Switch back to main content
                driver.switch_to.default_content()

        except Exception as e:
            logger.warning(f"Coderspace: Cloudflare click attempt failed: {e}")
            driver.switch_to.default_content()

        # Smart Wait: Wait for either event cards OR cloudflare challenge
        try:
            WebDriverWait(driver, 15).until(
                lambda d: len(
                    d.find_elements(
                        By.CSS_SELECTOR, "div.event-card, div.card, article"
                    )
                )
                > 0
            )
        except Exception:
            # Timeout is acceptable, we proceed to parse what we have (or fail gracefully)
            logger.warning("Coderspace: Timeout while waiting for page content.")
            pass

        # Parse Content
        page_source = driver.page_source

        # Cloudflare Check (UC usually bypasses this, but good to check)
        if "Verify you are human" in page_source or "cloudflare" in page_source.lower():
            logger.error("Coderspace: Cloudflare challenge still active despite UC!")
            # We might return empty or try to wait longer

        soup = BeautifulSoup(page_source, "html.parser")

        # Parsing Optimization: Single pass selector
        event_cards = soup.select("div.event-card, div.card, article")

        if not event_cards:
            # Fallback: Check for links if no cards (rare structure change)
            all_links = soup.find_all(
                "a", href=lambda x: x and "etkinlik" in str(x).lower()
            )
            logger.warning(
                f"Coderspace: No cards found. Found {len(all_links)} potential event links."
            )
            return []

        # Data Extraction
        for card in event_cards:
            try:
                # Optimized Selector: Determine title element in one go
                title_elem = card.select_one("h3, h2, h4")
                if not title_elem:
                    continue
                title = title_elem.get_text(strip=True)

                # Link Extraction
                link_elem = card.select_one("a[href]")
                if not link_elem:
                    continue
                href = str(link_elem["href"])
                # Fast string concatenation
                link_url = (
                    href if href.startswith("http") else f"https://coderspace.io{href}"
                )

                # Date
                date_elem = card.select_one("span.event-date, time")
                date_str = date_elem.get_text(strip=True) if date_elem else None

                # Description
                desc_elem = card.select_one("p.event-description, p")
                description = (
                    desc_elem.get_text(strip=True)
                    if desc_elem
                    else "Etkinlik açıklaması mevcut değil."
                )

                # Image
                img_elem = card.find("img")
                image_src = str(img_elem.get("src")) if img_elem else ""
                image_url = ""
                if image_src:
                    image_url = (
                        image_src
                        if image_src.startswith("http")
                        else f"https://coderspace.io{image_src}"
                    )

                events.append(
                    {
                        "title": title,
                        "url": link_url,
                        "date": date_str,
                        "description": description,
                        "image_url": image_url,
                        "source": "Coderspace",
                        "location": "Online",
                        "is_active": True,
                    }
                )

            except Exception as e:
                # Resilience: Log error but continue loop (don't fail batch)
                logger.error(f"Coderspace card parsing error: {e}", exc_info=False)
                continue

        return events

    except Exception as e:
        logger.error(f"Coderspace general error: {e}", exc_info=True)
        return []

    finally:
        # Resource Management: Ensure driver is released
        if driver:
            try:
                driver.quit()
            except Exception:
                pass
