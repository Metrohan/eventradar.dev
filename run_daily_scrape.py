import os
import sys
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed



logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir))
sys.path.insert(0, project_root)


from app import app
from services.scraper_service import process_scraped_events

from scrapers.techcareer_scraper import scrape_techcareer_events
from scrapers.cs_scraper import scrape_coderspace_events
from scrapers.anbean_scraper import scrape_anbean_events
from scrapers.kodluyoruz_scraper import scrape_kodluyoruz_events
from scrapers.youthall_scraper import scrape_youthall_events

SCRAPERS = {
    "TechCareer.net": scrape_techcareer_events,
    "Coderspace": scrape_coderspace_events,
    "Anbean": scrape_anbean_events,
    "Kodluyoruz": scrape_kodluyoruz_events,
    "Youthall": scrape_youthall_events,
}

def scrape_source(scraper_func, source_name):
    logging.info(f"\n--- {source_name} Scraper Başlatılıyor ---")
    try:
        if hasattr(scraper_func, '__name__'):
            logging.info(f"{source_name} etkinlikleri çekiliyor: {scraper_func.__module__}.{scraper_func.__name__}")
        else:
            logging.info(f"{source_name} etkinlikleri çekiliyor.")

        events = scraper_func()
        logging.info(f"{source_name}'ten {len(events)} etkinlik çekildi.")
        return events
    except Exception as e:
        logging.error(f"Hata: {source_name} scraper çalışırken bir sorun oluştu: {e}")
        import traceback
        traceback.print_exc()
        return []

def run_scraper_and_save_to_db():
    logging.info(f"--- Etkinlik Çekme Süreci Başlatıldı: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")

    with app.app_context():

        all_scraped_events = []
        with ThreadPoolExecutor(max_workers=len(SCRAPERS)) as executor:
            futures = {executor.submit(scrape_source, func, name): name for name, func in SCRAPERS.items()}

            for future in as_completed(futures):
                source_name = futures[future]
                try:
                    events = future.result()
                    if events:
                        all_scraped_events.extend(events)
                        logging.info(f"{source_name} scraper'ından {len(events)} etkinlik başarıyla çekildi.")
                    else:
                        logging.warning(f"{source_name} scraper'ından etkinlik çekilemedi veya bir hata oluştu.")
                except Exception as exc:
                    logging.error(f'{source_name} scraper çalışırken beklenmedik bir hata oluştu (ThreadPoolExecutor): {exc}')

        if all_scraped_events:
            logging.info("\n--- Tüm Çekilen Etkinlikler Veritabanına Kaydediliyor ---")
            process_scraped_events(all_scraped_events, "Tüm Kaynaklar")
        else:
            logging.warning("\nHiçbir etkinlik çekilemedi veya kaydedilecek etkinlik bulunamadı.")

        logging.info("\nVeritabanına kaydetme işlemi tamamlandı.")

    logging.info(f"\n--- Etkinlik Çekme Süreci Tamamlandı: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")


if __name__ == "__main__":
    run_scraper_and_save_to_db()