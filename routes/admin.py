from flask import render_template, redirect, url_for, flash, request, session, Blueprint
from models import Event, Announcement, Suggestion, EventRequest, PendingEvent, SimilarEventPair
from utils.auth import requires_auth

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route('/admin', methods=['GET', 'POST'])
def admin_login():
    from config import Config
    if request.method == 'POST':
        if request.form.get('username') == Config.ADMIN_USERNAME and request.form.get('password') == Config.ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin.dashboard'))
        flash('Hatalı kullanıcı adı veya şifre!')
    return render_template('admin_login.html')

@admin_bp.route('/dashboard')
@requires_auth
def dashboard():
    return render_template('dashboard.html',
                           events=Event.query.order_by(Event.date.desc()).all(),
                           announcements=Announcement.query.order_by(Announcement.created_at.desc()).all(),
                           requests=EventRequest.query.order_by(EventRequest.created_at.desc()).all(),
                           suggestions=Suggestion.query.order_by(Suggestion.created_at.desc()).all(),
                           pending_events=PendingEvent.query.all(),
                           similar_pairs=SimilarEventPair.query.all())

@admin_bp.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin.admin_login'))
