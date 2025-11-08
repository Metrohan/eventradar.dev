import os
import sys
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Proje kökünü path'e ekle
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.insert(0, project_root)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

from app.services.scraper_service import process_scraped_events, deactivate_past_events
from app.scrapers import (
    scrape_techcareer_events,
    scrape_coderspace_events,
    scrape_anbean_events,
    scrape_kodluyoruz_events,
    scrape_youthall_events
)

SCRAPERS = {
    "TechCareer.net": scrape_techcareer_events,
    "Coderspace": scrape_coderspace_events,
    "Anbean": scrape_anbean_events,
    "Kodluyoruz": scrape_kodluyoruz_events,
    "Youthall": scrape_youthall_events,
}

def scrape_source(scraper_func, source_name):
    """Tek bir kaynaktan scrape yap"""
    logging.info(f"--- {source_name} Scraper Başlatılıyor ---")
    try:
        events = scraper_func()
        logging.info(f"{source_name}'ten {len(events)} etkinlik çekildi")
        return events
    except Exception as e:
        logging.error(f"{source_name} hatası: {e}", exc_info=True)
        return []

def run_scraper_and_save_to_db():
    """Tüm scraper'ları çalıştır ve kaydet"""
    logging.info(f"=== Scraping Başladı: {datetime.now():%Y-%m-%d %H:%M:%S} ===")
    
    # Önce geçmiş etkinlikleri deaktive et
    logging.info("--- Geçmiş Etkinlikler Kontrol Ediliyor ---")
    deactivated = deactivate_past_events()
    if deactivated > 0:
        logging.info(f"✓ {deactivated} geçmiş etkinlik deaktive edildi")
    else:
        logging.info("✓ Deaktive edilecek geçmiş etkinlik yok")
    
    all_scraped_events = []
    
    # Selenium scraperları sırayla çalıştır (ChromeDriver çakışması önlemek için)
    # Önce static scraperlar (daha hızlı)
    static_scrapers = [("Kodluyoruz", scrape_kodluyoruz_events), ("Anbean", scrape_anbean_events)]
    for name, func in static_scrapers:
        events = scrape_source(func, name)
        if events:
            all_scraped_events.extend(events)
    
    # Sonra Selenium scraperlar sırayla
    selenium_scrapers = [
        ("TechCareer.net", scrape_techcareer_events),
        ("Youthall", scrape_youthall_events),
        ("Coderspace", scrape_coderspace_events)
    ]
    for name, func in selenium_scrapers:
        events = scrape_source(func, name)
        if events:
            all_scraped_events.extend(events)
    
    if all_scraped_events:
        logging.info(f"\n--- {len(all_scraped_events)} Etkinlik Kaydediliyor ---")
        result = process_scraped_events(all_scraped_events, "Tüm Kaynaklar")
        logging.info(f"✓ Veritabanına kaydedildi: {result}")
    else:
        logging.warning("✗ Kaydedilecek etkinlik yok")
    
    logging.info(f"=== Scraping Bitti: {datetime.now():%Y-%m-%d %H:%M:%S} ===")

if __name__ == "__main__":
    run_scraper_and_save_to_db()
