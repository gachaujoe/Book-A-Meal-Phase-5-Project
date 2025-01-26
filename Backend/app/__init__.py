from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from dotenv import load_dotenv
import os

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()

def create_app(config_Class='config.Config'):
    load_dotenv()
    app = Flask(__name__)
    app.config.from_object(config_Class)

    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    from app.routes import auth_bp, admin_bp, customer_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(customer_bp, url_prefix="/customer")

    return app
