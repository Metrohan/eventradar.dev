from flask import Blueprint, render_template, request, flash, redirect, url_for
from models import EventRequest
from datetime import datetime
from app import db
requests_bp = Blueprint("requests", __name__, url_prefix="/requests")

@requests_bp.route('/etkinlik-talep', methods=['GET', 'POST'])
def etkinlik_talep():
    if request.method == 'POST':
        try:
            event_link = request.form.get('event_link')
            event_title = request.form.get('event_title')
            event_date_str = request.form.get('event_date')
            event_description = request.form.get('event_description')
            
            event_date = datetime.strptime(event_date_str, '%Y-%m-%d') if event_date_str else None

            new_request = EventRequest(
                link=event_link,
                title=event_title,
                date=event_date,
                description=event_description
            )
            
            db.session.add(new_request)
            db.session.commit()
            
            flash('Etkinlik ekleme talebiniz başarıyla alındı. Teşekkür ederiz!', 'success')
            return redirect(url_for('requests.etkinlik_talep'))

        except Exception as e:
            db.session.rollback()
            flash(f'Talebiniz gönderilirken bir hata oluştu: {e}', 'error')
            
    return render_template('etkinlik_talep.html')