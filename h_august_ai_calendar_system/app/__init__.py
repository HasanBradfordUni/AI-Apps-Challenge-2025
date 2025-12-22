from flask import Flask
import os

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    app.config['GOOGLE_CALENDAR_CREDENTIALS'] = os.environ.get('GOOGLE_CALENDAR_CREDENTIALS')
    app.config['OUTLOOK_CLIENT_ID'] = os.environ.get('OUTLOOK_CLIENT_ID')
    app.config['OUTLOOK_CLIENT_SECRET'] = os.environ.get('OUTLOOK_CLIENT_SECRET')
    
    # Register blueprints
    from .routes import calendar_bp
    app.register_blueprint(calendar_bp)
    
    return app