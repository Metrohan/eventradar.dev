from datetime import datetime
from sqlalchemy.exc import IntegrityError
from extensions import db
from models import Event, PendingEvent
from config import Config
from flask import current_app as app
import dateparser

def process_scraped_events(events_data, default_source="Scraper"):
    added_count = 0
    skipped_count = 0
    
    for event_data in events_data:
        try:
            # 1. URL zaten var mı kontrol et
            if Event.query.filter_by(url=event_data['url']).first() or PendingEvent.query.filter_by(url=event_data['url']).first():
                app.logger.info(f"Etkinlik URL'si zaten mevcut, atlanıyor: {event_data['url']}")
                skipped_count += 1
                continue

            # 2. Etkinliği doğrudan ekle
            event_date = None
            if 'date' in event_data and event_data['date']:
                try:
                    event_date = dateparser.parse(event_data['date'], languages=['tr'])
                except ValueError:
                    app.logger.warning(f"Geçersiz tarih formatı: {event_data['date']}")

            db.session.add(Event(
                title=event_data['title'],
                description=event_data.get('description'),
                date=event_date,
                location=event_data.get('location'),
                url=event_data['url'],
                image_url=event_data.get('image_url'),
                source=event_data.get('source', default_source),
                is_active=True,
                scraped_at=datetime.now()
            ))
            added_count += 1

            db.session.commit()

        except IntegrityError:
            db.session.rollback()
            app.logger.warning(f"URL benzersizlik hatası, atlanıyor: {event_data['url']}")
            skipped_count += 1
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Etkinlik kaydedilirken hata oluştu: {event_data.get('title', 'N/A')} - {e}")
            skipped_count += 1

    return added_count, skipped_count
