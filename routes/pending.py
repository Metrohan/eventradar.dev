from flask import Blueprint, render_template, redirect, url_for, flash
from datetime import datetime
from extensions import db
from models import PendingEvent, Event, SimilarEventPair
from utils.auth import requires_auth
pending_bp = Blueprint("pending", __name__, url_prefix="/pending")

@pending_bp.route('/admin/pending_events')
@requires_auth
def view_pending_events():
    return render_template('pending_events.html', pending_events=PendingEvent.query.all(), similar_pairs=SimilarEventPair.query.all())

@pending_bp.route('/admin/pending_events/approve/<int:pending_id>', methods=['POST'])
@requires_auth
def approve_pending_event(pending_id):
    pending_event = PendingEvent.query.get_or_404(pending_id)
    try:
        new_event = Event(
            title=pending_event.title, description=pending_event.description, date=pending_event.date,
            location=pending_event.location, url=pending_event.url, image_url=pending_event.image_url,
            source=pending_event.source, is_active=True, scraped_at=datetime.now()
        )
        db.session.add(new_event)
        SimilarEventPair.query.filter_by(pending_event_id=pending_id).delete()
        db.session.delete(pending_event)
        db.session.commit()
        flash(f"'{new_event.title}' etkinliği başarıyla eklendi.", 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Onaylama sırasında hata oluştu: {e}', 'error')
    return redirect(url_for('pending.view_pending_events'))

@pending_bp.route('/admin/pending_events/reject/<int:pending_id>', methods=['POST'])
@requires_auth
def reject_pending_event(pending_id):
    pending_event = PendingEvent.query.get_or_404(pending_id)
    try:
        SimilarEventPair.query.filter_by(pending_event_id=pending_id).delete()
        db.session.delete(pending_event)
        db.session.commit()
        flash(f"'{pending_event.title}' etkinliği reddedildi.", 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Reddetme sırasında hata oluştu: {e}', 'error')
    return redirect(url_for('pending.view_pending_events'))
