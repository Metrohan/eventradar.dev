import os
import sys
import logging
from datetime import datetime

# Proje kökünü path'e ekle
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.insert(0, project_root)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

from app.services.event_ingestion import build_event_ingestion
from app.services.scrape_run import build_scrape_run_coordinator


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

    results = build_scrape_run_coordinator().run_all()
    for result in results:
        if result.status == "success":
            logging.info(
                "✓ %s: fetched=%d new=%d updated=%d failed=%d deactivated=%d",
                result.source,
                result.fetched,
                result.new,
                result.updated,
                result.failed,
                result.deactivated,
            )
        else:
            logging.error("✗ %s: %s", result.source, result.error)

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
