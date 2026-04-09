from flask import Blueprint, render_template, redirect, url_for, flash, request
from extensions import db
from models import Suggestion
from utils.auth import requires_auth
suggestions_bp = Blueprint("suggestions", __name__, url_prefix="/suggestions")

@suggestions_bp.route('/oneri_sikayet', methods=['GET', 'POST'])
def oneri_sikayet():
    if request.method == 'POST':
        suggestion_type = request.form.get('request_type')
        suggestion_title = request.form.get('event_title')
        suggestion_text = request.form.get('event_description')
        if not suggestion_type or not suggestion_title or not suggestion_text:
            flash('Lütfen tüm alanları doldurun.', 'error')
            return redirect(url_for('suggestions.oneri_sikayet'))
        try:
            new_suggestion = Suggestion(suggestion_type=suggestion_type, suggestion_title=suggestion_title, suggestion_text=suggestion_text)
            db.session.add(new_suggestion)
            db.session.commit()
            flash('Öneri/Şikayetiniz başarıyla gönderildi.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Hata oluştu: {e}', 'error')
        return redirect(url_for('suggestions.oneri_sikayet'))
    return render_template('oneri_sikayet.html')

@suggestions_bp.route('/suggestions')
@requires_auth
def view_suggestions():
    suggestions = Suggestion.query.order_by(Suggestion.id.desc()).all()
    return render_template('suggestion.html', suggestions=suggestions)
