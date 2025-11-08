import sys, os, time
sys.path.insert(0, '/app')
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

def find_chromedriver():
    cache_dir = os.path.expanduser("~/.wdm/drivers/chromedriver")
    if os.path.exists(cache_dir):
        versions = os.listdir(cache_dir)
        if versions:
            latest = sorted(versions)[-1]
            driver_dir = os.path.join(cache_dir, latest)
            for root, dirs, files in os.walk(driver_dir):
                for file in files:
                    if file == "chromedriver":
                        driver_path = os.path.join(root, file)
                        os.chmod(driver_path, 0o755)
                        return driver_path
    return None

driver_path = find_chromedriver()
if not driver_path:
    from webdriver_manager.chrome import ChromeDriverManager
    ChromeDriverManager().install()
    driver_path = find_chromedriver()

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

service = Service(executable_path=driver_path)
driver = webdriver.Chrome(service=service, options=options)

print("=== YOUTHALL ===")
driver.get("https://www.youthall.com/tr/events")
time.sleep(8)
soup = BeautifulSoup(driver.page_source, "html.parser")

# Event row'ları bul
event_rows = soup.find_all('div', class_='event-row')
print(f'Total event-row divs: {len(event_rows)}')

if event_rows:
    for idx, row in enumerate(event_rows[:3]):
        print(f'\n=== Event {idx} ===')
        
        # Başlık
        title = row.find('h3') or row.find('h2') or row.find('h4')
        if title:
            print(f'  Title: {title.get_text(strip=True)[:80]}')
        
        # Link
        link = row.find('a', href=True)
        if link:
            print(f'  Link: {link.get("href")}')
        
        # Date
        date_box = row.find('div', class_='events__content__datebox')
        if date_box:
            print(f'  Date: {date_box.get_text(strip=True)}')
        
        # Image
        img = row.find('img')
        if img:
            print(f'  Image: {img.get("src")[:100]}')
        
        # Description
        details = row.find('div', class_='events__content__details')
        if details:
            desc_text = details.get_text(strip=True)
            print(f'  Description: {desc_text[:120]}')

driver.quit()

print("\n\n=== CODERSPACE ===")
options2 = Options()
options2.add_argument("--headless")
options2.add_argument("--no-sandbox")
options2.add_argument("--disable-dev-shm-usage")
service2 = Service(executable_path=driver_path)
driver = webdriver.Chrome(service=service2, options=options2)
driver.get("https://coderspace.io/etkinlikler")
time.sleep(8)
cs_soup = BeautifulSoup(driver.page_source, "html.parser")

# Try to find main content
body_text = cs_soup.get_text(strip=True)
print(f"Body text length: {len(body_text)}")
print(f"Sample: {body_text[:500]}")

# Look for any data attributes or script tags with JSON
scripts = cs_soup.find_all('script')
print(f"\nScript tags: {len(scripts)}")
for script in scripts[:5]:
    text = script.get_text()
    if 'etkinlik' in text.lower() or 'event' in text.lower():
        print(f"  Found relevant script: {text[:200]}")

driver.quit()

