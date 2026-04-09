from flask import Flask
from config import Config
from extensions import db
from routes import public_bp, admin_bp, events_bp, announcements_bp, suggestions_bp, pending_bp, requests_bp
from utils.filters import datetimeformat

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    # Blueprintleri kaydet
    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(announcements_bp)
    app.register_blueprint(suggestions_bp)
    app.register_blueprint(pending_bp)
    app.register_blueprint(requests_bp)

    # Template filtreleri ekle
    app.jinja_env.filters['datetimeformat'] = datetimeformat

    # Veritabanı tablolarını oluştur
    with app.app_context():
        db.create_all()

    return app

# Gunicorn ve Flask CLI'nin bulabilmesi için doğrudan app nesnesi
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
