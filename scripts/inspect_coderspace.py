from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time, os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

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

print("=== CODERSPACE ===")
driver.get("https://coderspace.io/etkinlikler")
time.sleep(8)  # Longer wait for SPA
soup = BeautifulSoup(driver.page_source, "html.parser")

# Save HTML for debugging
with open("/tmp/coderspace_page.html", "w", encoding="utf-8") as f:
    f.write(soup.prettify())
print("Saved page HTML to /tmp/coderspace_page.html")

# Find all unique class names
all_classes = set()
for tag in soup.find_all(True):
    if tag.get('class'):
        all_classes.update(tag.get('class'))

event_related = [c for c in all_classes if 'event' in c.lower() or 'card' in c.lower() or 'item' in c.lower()]
print(f"Event-related classes: {sorted(event_related)[:10]}")

# Find links
links = soup.find_all("a", href=lambda x: x and "etkinlik" in x.lower())
print(f"\nLinks with 'etkinlik': {len(links)}")
if links:
    for i, link in enumerate(links[:3]):
        print(f"  [{i}] {link.get('href')} - {link.get_text(strip=True)[:60]}")

# Try to find any structure
articles = soup.find_all("article")
print(f"\nArticles: {len(articles)}")

sections = soup.find_all("section")
print(f"Sections: {len(sections)}")

driver.quit()

print("\n=== YOUTHALL ===")
options2 = Options()
options2.add_argument("--headless")
options2.add_argument("--no-sandbox")
options2.add_argument("--disable-dev-shm-usage")
service2 = Service(executable_path=driver_path)
driver = webdriver.Chrome(service=service2, options=options2)
driver.get("https://www.youthall.com/tr/events")
time.sleep(8)
soup = BeautifulSoup(driver.page_source, "html.parser")

# Save HTML for debugging
with open("/tmp/youthall_page.html", "w", encoding="utf-8") as f:
    f.write(soup.prettify())

# Find all unique class names
all_classes = set()
for tag in soup.find_all(True):
    if tag.get('class'):
        all_classes.update(tag.get('class'))

event_related = [c for c in all_classes if 'event' in c.lower() or 'card' in c.lower() or 'item' in c.lower()]
print(f"Event-related classes: {sorted(event_related)[:10]}")

# Find links
links = soup.find_all("a", href=lambda x: x and "/event" in x.lower())
print(f"\nLinks with '/event': {len(links)}")
if links:
    for i, link in enumerate(links[:3]):
        print(f"  [{i}] {link.get('href')} - {link.get_text(strip=True)[:60]}")

articles = soup.find_all("article")
print(f"\nArticles: {len(articles)}")

driver.quit()
