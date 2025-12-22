from flask import Flask
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this to a secure value
    
    # Initialize CSRF protection
    csrf.init_app(app)
    
    # Register blueprints
    from app.routes import app as main_blueprint
    app.register_blueprint(main_blueprint)
    
    # Properly exempt specific routes from CSRF protection
    csrf.exempt('main_blueprint.process_text_section')
    csrf.exempt('main_blueprint.process_cv')
    
    return app