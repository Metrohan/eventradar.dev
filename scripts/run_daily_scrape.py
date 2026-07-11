import os
import sys
import logging
import time
from datetime import datetime

# Proje kökünü path'e ekle
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.insert(0, project_root)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

from app.services.event_ingestion import ScrapedEvent, build_event_ingestion
from app.services.source_catalog import get_enabled_sources


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
        return None


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
    ingestion = build_event_ingestion()

    # Önce geçmiş etkinlikleri deaktive et
    logging.info("--- Geçmiş Etkinlikler Kontrol Ediliyor ---")
    deactivated = ingestion.deactivate_past()
    if deactivated > 0:
        logging.info(f"✓ {deactivated} geçmiş etkinlik deaktive edildi")
    else:
        logging.info("✓ Deaktive edilecek geçmiş etkinlik yok")

    total_events = 0

    # Selenium scraperları sırayla çalıştır (ChromeDriver çakışması önlemek için)

    # Önce static scraperlar (daha hızlı)
    for source in get_enabled_sources():
        events = scrape_source(source.runner, source.name)
        if events is None:
            continue

        total_events += len(events)
        result = ingestion.ingest(
            ScrapedEvent.from_mapping(event, source.name) for event in events
        )
        reconciled = ingestion.reconcile_source(source.name)
        logging.info(f"✓ {source.name}: {result.summary()}, Reconciled: {reconciled}")

    if total_events == 0:
        logging.warning("✗ Kaydedilecek etkinlik yok")

    # Scraper kaynakları geçmiş tarihli kayıtları hâlâ döndürebilir. Kayıt
    # işleminden sonra tekrar temizleyerek bu etkinliklerin aktif kalmasını önle.
    deactivated_after_scrape = ingestion.deactivate_past()
    if deactivated_after_scrape > 0:
        logging.info(
            f"✓ Tarama sonrası {deactivated_after_scrape} geçmiş etkinlik deaktive edildi"
        )

    logging.info(f"=== Scraping Bitti: {datetime.now():%Y-%m-%d %H:%M:%S} ===")


if __name__ == "__main__":
    run_scraper_and_save_to_db()
