from datetime import datetime, date
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.event import Event
import logging
import dateparser

logger = logging.getLogger(__name__)

def deactivate_past_events():
    """
    Tarihi geçmiş etkinlikleri otomatik olarak deaktive et
    
    Returns:
        int: Deaktive edilen etkinlik sayısı
    """
    db = SessionLocal()
    deactivated_count = 0
    
    try:
        today = date.today()
        # Tarihi geçmiş VE hala aktif olan etkinlikleri bul
        past_events = db.query(Event).filter(
            Event.date < today,
            Event.is_active == True
        ).all()
        
        for event in past_events:
            event.is_active = False
            deactivated_count += 1
            logger.info(f"Deaktive edildi (tarihi geçti): {event.title} ({event.date})")
        
        if deactivated_count > 0:
            db.commit()
            logger.info(f"Toplam {deactivated_count} geçmiş etkinlik deaktive edildi")
        
        return deactivated_count
        
    except Exception as e:
        logger.error(f"Geçmiş etkinlikler deaktive edilirken hata: {e}")
        db.rollback()
        return 0
    finally:
        db.close()

def process_scraped_events(events_data: list, source_name: str = "Scraper"):
    """
    Scraped events'leri veritabanına kaydet
    
    Args:
        events_data: Etkinlik verisi listesi
        source_name: Kaynak adı (varsayılan: "Scraper")
        
    Returns:
        dict: {"added": int, "skipped": int}
    """
    db = SessionLocal()
    added_count = 0
    skipped_count = 0
    
    try:
        for event_data in events_data:
            try:
                # URL kontrolü (tekrar kontrolü)
                url = event_data.get('url') or event_data.get('link')
                if not url:
                    logger.warning(f"URL bulunamadı, atlanıyor: {event_data.get('title', 'N/A')}")
                    skipped_count += 1
                    continue
                
                existing_event = db.query(Event).filter(Event.url == url).first()
                if existing_event:
                    logger.info(f"Etkinlik URL'si zaten mevcut, atlanıyor: {url}")
                    skipped_count += 1
                    continue

                # Tarih parse et
                event_date = None
                date_str = event_data.get('date')
                if date_str:
                    try:
                        # Eğer zaten datetime objesi ise direkt kullan
                        if isinstance(date_str, datetime):
                            event_date = date_str
                        else:
                            # String ise parse et
                            event_date = dateparser.parse(str(date_str), languages=['tr', 'en'])
                        logger.debug(f"Tarih parse edildi: {date_str} -> {event_date}")
                    except Exception as e:
                        logger.warning(f"Geçersiz tarih formatı: {date_str} - {e}")

                # Yeni event oluştur
                new_event = Event(
                    title=event_data.get('title'),
                    description=event_data.get('description'),
                    date=event_date,
                    location=event_data.get('location'),
                    url=url,
                    image_url=event_data.get('image_url'),
                    source=event_data.get('source', source_name),
                    is_active=True,
                    scraped_at=datetime.utcnow()
                )
                
                db.add(new_event)
                db.commit()
                added_count += 1
                logger.debug(f"Etkinlik eklendi: {new_event.title}")

            except IntegrityError as e:
                db.rollback()
                logger.warning(f"Veritabanı IntegrityError: {event_data.get('title', 'N/A')} - {e}")
                skipped_count += 1
            except Exception as e:
                db.rollback()
                logger.error(f"Etkinlik kaydedilirken hata: {event_data.get('title', 'N/A')} - {e}", exc_info=True)
                skipped_count += 1
        
        logger.info(f"{source_name}: {added_count} yeni, {skipped_count} atlandı")
        return {"added": added_count, "skipped": skipped_count}
        
    except Exception as e:
        db.rollback()
        logger.error(f"process_scraped_events genel hatası ({source_name}): {e}", exc_info=True)
        raise
    finally:
        db.close()
