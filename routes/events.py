from flask import render_template, redirect, url_for, flash, request, Blueprint
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from extensions import db
from models import Event, EventRequest
from utils.auth import requires_auth
events_bp = Blueprint("events", __name__, url_prefix="/events")

@events_bp.route('/add_event', methods=['GET', 'POST'])
@requires_auth
def add_event():
    if request.method == 'POST':
        title = request.form.get('title')
        date_str = request.form.get('date')
        description = request.form.get('description')
        url = request.form.get('url')
        location = request.form.get('location')
        image_url = request.form.get('image_url')
        source = request.form.get('source')
        is_active = request.form.get('is_active') == 'on'

        if not title or not url:
            flash('Başlık ve URL zorunludur!', 'error')
            return redirect(url_for('events.add_event'))

        try:
            event_date = datetime.strptime(date_str.replace('T', ' '), '%Y-%m-%d %H:%M') if date_str else None
            new_event = Event(
                title=title, description=description, date=event_date, location=location,
                url=url, image_url=image_url, source=source or 'Admin',
                is_active=is_active, scraped_at=datetime.now()
            )
            db.session.add(new_event)
            db.session.commit()
            flash('Etkinlik başarıyla eklendi.', 'success')
            return redirect(url_for('admin.dashboard'))
        except IntegrityError:
            db.session.rollback()
            flash('Aynı URL ile zaten kayıtlı bir etkinlik var.', 'error')
        except Exception as e:
            db.session.rollback()
            flash(f'Hata oluştu: {e}', 'error')

    return render_template('add_event.html')

@events_bp.route('/edit_event/<int:event_id>', methods=['GET', 'POST'])
@requires_auth
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    if request.method == 'POST':
        title = request.form.get('title')
        date_str = request.form.get('date')
        description = request.form.get('description')
        url = request.form.get('url')
        location = request.form.get('location')
        image_url = request.form.get('image_url')
        source = request.form.get('source')
        is_active = request.form.get('is_active') == 'on'

        if not title or not url:
            flash('Başlık ve URL zorunludur!', 'error')
            return redirect(url_for('events.edit_event', event_id=event_id))

        try:
            event.date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M') if date_str else None
            event.title, event.description, event.location, event.url = title, description, location, url
            event.image_url, event.source, event.is_active = image_url, source or 'Admin', is_active
            event.scraped_at = datetime.now()
            db.session.commit()
            flash('Etkinlik başarıyla güncellendi.', 'success')
            return redirect(url_for('admin.dashboard'))
        except IntegrityError:
            db.session.rollback()
            flash('Aynı URL ile zaten kayıtlı bir etkinlik var.', 'error')
        except Exception as e:
            db.session.rollback()
            flash(f'Hata oluştu: {e}', 'error')

    return render_template('edit_event.html', event=event, event_date_str=event.date.strftime('%Y-%m-%d %H:%M') if event.date else '')

@events_bp.route('/delete_event/<int:event_id>', methods=['POST'])
@requires_auth
def delete_event(event_id):
    event = Event.query.get(event_id)
    if event:
        db.session.delete(event)
        db.session.commit()
        flash('Etkinlik silindi.', 'success')
    else:
        flash('Etkinlik bulunamadı.', 'error')
    return redirect(url_for('admin.dashboard'))

@events_bp.route('/requests')
@requires_auth
def view_requests():
    requests = EventRequest.query.order_by(EventRequest.created_at.desc()).all()
    return render_template('requests.html', requests=requests)
