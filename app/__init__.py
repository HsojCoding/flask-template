from flask import Flask
from app.views import main_bp, auth_bp
from app.auth import login_manager, bcrypt
from app.db import db, migrate
from app.db.models import *

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config['SECRET_KEY'] = 'placeholder_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///proto.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    return app