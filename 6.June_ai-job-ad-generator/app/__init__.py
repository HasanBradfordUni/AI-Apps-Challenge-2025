from flask import Flask
from flask_wtf import CSRFProtect
# Register the blueprint
from .routes import app as routes_blueprint

csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key_here'  # Set your secret key here
    app.config['JSON_AS_ASCII'] = False
    app.config['JSONIFY_MIMETYPE'] = 'application/json'

    csrf.init_app(app)
    app.register_blueprint(routes_blueprint)

    with app.app_context():
        from . import routes

    return app