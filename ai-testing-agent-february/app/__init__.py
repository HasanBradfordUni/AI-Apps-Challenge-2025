from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

db = SQLAlchemy()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    app.config.from_object('instance.config.Config')

    db.init_app(app)
    csrf.init_app(app)

    with app.app_context():
        from . import routes, models, forms
        db.create_all()

    # Register the blueprint
    from .routes import app as routes_blueprint
    app.register_blueprint(routes_blueprint)

    return app