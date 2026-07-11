import os
import sys
import logging
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Proje kökünü path'e ekle
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.insert(0, project_root)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

from app.services.scraper_service import process_scraped_events, deactivate_past_events

from app.scrapers import (
    scrape_techcareer_events,
    scrape_coderspace_events,
    scrape_anbean_events,
    scrape_kodluyoruz_events,
    scrape_youthall_events,
)
from app.scrapers.akbank_scraper import scrape_akbank_events
from app.scrapers.pupilica_scraper import scrape_pupilica_events
from app.scrapers.techistanbul_scraper import scrape_techistanbul_events

SCRAPERS = {
    "TechCareer.net": scrape_techcareer_events,
    "Coderspace": scrape_coderspace_events,
    "Anbean": scrape_anbean_events,
    "Kodluyoruz": scrape_kodluyoruz_events,
    "Youthall": scrape_youthall_events,
    "Akbank Gençlik Akademisi": scrape_akbank_events,
    "Pupilica": scrape_pupilica_events,
    "Tech Istanbul": scrape_techistanbul_events,
}


def scrape_source(scraper_func, source_name):
    """Tek bir kaynaktan scrape yap ve sonucu scraper_logs'a kaydet"""
    logging.info(f"--- {source_name} Scraper Başlatılıyor ---")
    start_time = time.time()
    try:
        events = scraper_func()
        duration = time.time() - start_time
        logging.info(f"{source_name}'ten {len(events)} etkinlik çekildi")
        _log_scraper_run(source_name, "success", len(events), duration, None)
        return events
    except Exception as e:
        duration = time.time() - start_time
        logging.error(f"{source_name} hatası: {e}", exc_info=True)
        _log_scraper_run(source_name, "failed", 0, duration, str(e))
        return []


def _log_scraper_run(source_name, status, events_found, duration, error_message):
    """Tek bir kaynağın sonucunu scraper_logs tablosuna yazar (admin panelin
    Scraper Kontrol Merkezi'nin cron ile yapılan günlük taramaları da
    görebilmesi için — manuel tetikleme dışında hiçbir yer log yazmıyordu)."""
    from app.core.database import SessionLocal
    from app.services.scraper_service import ScraperService
    from app.schemas.scraper_log import ScraperLogCreate

    db = SessionLocal()
    try:
        ScraperService(db).create_log(
            ScraperLogCreate(
                source=source_name,
                status=status,
                events_found=events_found,
                new_events=0,
                error_message=error_message,
                duration_seconds=duration,
            )
        )
    except Exception as log_err:
        logging.error(f"Scraper log kaydedilemedi ({source_name}): {log_err}")
    finally:
        db.close()


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
    static_scrapers = [
        ("Kodluyoruz", scrape_kodluyoruz_events),
        ("Anbean", scrape_anbean_events),
        ("Akbank Gençlik Akademisi", scrape_akbank_events),
        ("Pupilica", scrape_pupilica_events),
        ("Tech Istanbul", scrape_techistanbul_events),
    ]
    for name, func in static_scrapers:
        events = scrape_source(func, name)
        if events:
            all_scraped_events.extend(events)

    # Sonra Selenium scraperlar sırayla
    selenium_scrapers = [
        ("TechCareer.net", scrape_techcareer_events),
        ("Youthall", scrape_youthall_events),
        ("Coderspace", scrape_coderspace_events),
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
