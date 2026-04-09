from flask import Blueprint, render_template, redirect, url_for, flash, request
from datetime import datetime
from extensions import db
from models import Announcement
from utils.auth import requires_auth
announcements_bp = Blueprint("announcements", __name__, url_prefix="/announcements")

@announcements_bp.route('/add_announcement', methods=['GET', 'POST'])
@requires_auth
def add_announcement():
    if request.method == 'POST':
        title = request.form.get('title')
        message = request.form.get('message')
        if not title or not message:
            flash('Duyuru başlığı ve mesajı gereklidir.', 'error')
            return redirect(url_for('admin.dashboard'))

        try:
            new_announcement = Announcement(title=title, message=message, created_at=datetime.now())
            db.session.add(new_announcement)
            db.session.commit()
            flash('Duyuru başarıyla eklendi.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Hata oluştu: {e}', 'error')

        return redirect(url_for('admin.dashboard'))
    return render_template('add_announcement.html')

@announcements_bp.route('/delete_announcement/<int:announcement_id>', methods=['POST'])
@requires_auth
def delete_announcement(announcement_id):
    announcement = Announcement.query.get_or_404(announcement_id)
    try:
        db.session.delete(announcement)
        db.session.commit()
        flash('Duyuru silindi.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Hata oluştu: {e}', 'error')
    return redirect(url_for('admin.dashboard'))
