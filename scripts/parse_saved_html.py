# === PUPILICA ===
print("=== PUPILICA ===")
driver.get("https://pupilica.com/events")
time.sleep(8)
pupilica_soup = BeautifulSoup(driver.page_source, "html.parser")
events = pupilica_soup.find_all("div", class_="event-card")
print(f"Pupilica: {len(events)} etkinlik bulundu.")
for idx, event in enumerate(events[:3]):
    title = event.find("h3") or event.find("h2")
    title = title.get_text(strip=True) if title else "Başlık yok"
    desc = event.find("div", class_="event-description")
    desc_text = desc.get_text(strip=True) if desc else ""
    date = event.find("div", class_="event-date")
    date_text = date.get_text(strip=True) if date else ""
    # Fallback: try to extract date from description
    if not date_text and desc_text:
        from app.services.date_extractor import extract_date_from_text

        date_text = extract_date_from_text(desc_text) or "Tarih belirtilmemiş"
    loc = event.find("div", class_="event-location")
    location = loc.get_text(strip=True) if loc else ""
    if not location and desc_text:
        # Try to infer location from description
        if "online" in desc_text.lower():
            location = "Online"
        else:
            location = "Konum belirtilmemiş"
    print(f"  {idx+1}. {title} | {date_text} | {location}")
print("Fetched Pupilica events page.")


# === AKBANK GENÇLİK AKADEMİSİ ===
print("\n\n=== AKBANK GENÇLİK AKADEMİSİ ===")
driver.get("https://www.akbankgenclikakademisi.com/etkinlik-takvimi")
time.sleep(8)
akbank_soup = BeautifulSoup(driver.page_source, "html.parser")
events = akbank_soup.find_all("div", class_="event-card")
print(f"Akbank: {len(events)} etkinlik bulundu.")
for idx, event in enumerate(events[:3]):
    title = event.find("h3") or event.find("h2")
    title = title.get_text(strip=True) if title else "Başlık yok"
    desc = event.find("div", class_="event-description")
    desc_text = desc.get_text(strip=True) if desc else ""
    date = event.find("div", class_="event-date")
    date_text = date.get_text(strip=True) if date else ""
    if not date_text and desc_text:
        from app.services.date_extractor import extract_date_from_text

        date_text = extract_date_from_text(desc_text) or "Tarih belirtilmemiş"
    loc = event.find("div", class_="event-location")
    location = loc.get_text(strip=True) if loc else ""
    if not location and desc_text:
        if "online" in desc_text.lower():
            location = "Online"
        else:
            location = "Konum belirtilmemiş"
    print(f"  {idx+1}. {title} | {date_text} | {location}")
print("Fetched Akbank Gençlik Akademisi events page.")


# === YOUTHALL (NEW LINK) ===
print("\n\n=== YOUTHALL (NEW LINK) ===")
driver.get("https://www.youthall.com/tr/events/all")
time.sleep(8)
youthall_soup = BeautifulSoup(driver.page_source, "html.parser")
event_rows = youthall_soup.find_all("div", class_="event-row")
print(f"Youthall: {len(event_rows)} etkinlik bulundu.")
from app.services.date_extractor import extract_date_from_text

for idx, row in enumerate(event_rows[:3]):
    title = row.find("h3") or row.find("h2") or row.find("h4")
    title = title.get_text(strip=True) if title else "Başlık yok"
    date_box = row.find("div", class_="events__content__datebox")
    date_text = date_box.get_text(strip=True) if date_box else ""
    details = row.find("div", class_="events__content__details")
    desc_text = details.get_text(strip=True) if details else ""
    if not date_text and desc_text:
        date_text = extract_date_from_text(desc_text) or "Tarih belirtilmemiş"
    location = ""
    if desc_text:
        if "online" in desc_text.lower():
            location = "Online"
        else:
            location = "Konum belirtilmemiş"
    else:
        location = "Konum belirtilmemiş"
    print(f"  {idx+1}. {title} | {date_text} | {location}")
print("Fetched Youthall events page (all).")

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
scripts = cs_soup.find_all("script")
print(f"\nScript tags: {len(scripts)}")
for script in scripts[:5]:
    text = script.get_text()
    if "etkinlik" in text.lower() or "event" in text.lower():
        print(f"  Found relevant script: {text[:200]}")

driver.quit()
