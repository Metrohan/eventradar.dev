from flask import Blueprint, render_template, redirect, url_for, flash, jsonify
from datetime import datetime
from models import Event, Announcement, EventRequest, Suggestion

# Burada Blueprint TANIMLANIYOR
public_bp = Blueprint("public", __name__, url_prefix="/")

@public_bp.route('/')
def index_redirect():
    return redirect(url_for('public.get_events'))

@public_bp.route('/events', methods=['GET'])
def get_events():
    announcement = Announcement.query.order_by(Announcement.created_at.desc()).first()
    try:
        events = Event.query.order_by(Event.date.desc()).all()
        events_for_template = []

        for event in events:
            event_image_url = event.image_url if event.image_url else url_for('static', filename='images/placeholder-image-colored.jpeg')
            events_for_template.append({
                'id': event.id,
                'title': event.title,
                'description': event.description,
                'date': event.date.strftime('%Y-%m-%dT%H:%M') if event.date else None,
                'location': event.location,
                'url': event.url,
                'source': event.source,
                'is_active': event.is_active,
                'scraped_at': event.scraped_at.strftime('%Y-%m-%d %H:%M:%S'),
                'image_url': event_image_url,
                'status': "Açık" if event.is_active else "Kapalı",
                'status_class': "acik" if event.is_active else "kapali"
            })

        last_updated_event = Event.query.order_by(Event.scraped_at.desc()).first()
        last_updated = last_updated_event.scraped_at.strftime('%Y-%m-%d %H:%M:%S') if last_updated_event else "N/A"
        total_active_events = Event.query.filter_by(is_active=True).count()

        return render_template('index.html',
                               grouped_events={"Tüm Etkinlikler": events_for_template},
                               last_updated=last_updated,
                               total_event_count=total_active_events,
                               announcement=announcement,
                               events=events)
    except Exception as e:
        flash('Etkinlikler yüklenirken bir sorun oluştu.', 'error')
        return render_template('index.html', grouped_events={}, last_updated="N/A", total_event_count=0)

@public_bp.route('/api/events')
def api_get_events():
    events = Event.query.filter_by(is_active=True).all()
    return jsonify([{
        'id': e.id,
        'title': e.title,
        'description': e.description,
        'date': e.date.isoformat() if e.date else None,
        'location': e.location,
        'url': e.url,
        'image_url': e.image_url,
        'source': e.source,
        'scraped_at': e.scraped_at.isoformat()
    } for e in events])

@public_bp.route('/api/announcements')
def api_get_announcements():
    anns = Announcement.query.order_by(Announcement.created_at.desc()).all()
    return jsonify([{
        'id': a.id,
        'title': a.title,
        'message': a.message,
        'created_at': a.created_at.isoformat()
    } for a in anns])
