from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import os


def find_chromedriver():
    # Reuse the logic from youthall_scraper.py or just use the system one
    # Attempt to use the one we found earlier if possible, or reliance on path
    paths = [
        "/usr/bin/chromedriver",
        "/usr/local/bin/chromedriver",
        "/root/.local/share/undetected_chromedriver/undetected_chromedriver",
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    return None


def test_youthall():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Try UC if available, else standard
    try:
        import undetected_chromedriver as uc
        from app.scrapers.cs_scraper import get_chrome_options

        options = get_chrome_options()
        driver = uc.Chrome(
            options=options,
            use_subprocess=True,
            version_main=144,
            driver_executable_path="/root/.local/share/undetected_chromedriver/undetected_chromedriver",
        )
    except ImportError:
        print("UC not found, using standard Selenium")
        driver_path = find_chromedriver()
        if driver_path:
            service = Service(executable_path=driver_path)
            driver = webdriver.Chrome(service=service, options=options)
        else:
            driver = webdriver.Chrome(options=options)

    try:
        print("Visiting Youthall...")
        driver.get("https://www.youthall.com/tr/events")
        time.sleep(10)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        cards = soup.find_all("div", class_="event-row")
        print(f"Found {len(cards)} cards.")

        for i, card in enumerate(cards[:5]):
            print(f"--- Event {i+1} ---")

            # Check for the description/subtitle class
            # The current scraper uses 'events__content__details'
            # But let's print generic structure to be sure

            details = card.find("div", class_="events__content__details")
            if details:
                print(f"Details Text: '{details.text.strip()}'")
            else:
                print("Details div not found.")

            # Also check datebox
            datebox = card.find("div", class_="events__content__datebox")
            if datebox:
                print(f"Datebox: '{datebox.text.strip()}'")

            # Check for other potential elements that might contain the string
            # "12 Şubat Perşembe, 12:00 Söğütözü/Ankara - Ankara"
            # It might be in a p tag or span
            print("Full Text Cleaned:", " ".join(card.get_text(strip=True).split()))

    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()


if __name__ == "__main__":
    test_youthall()
