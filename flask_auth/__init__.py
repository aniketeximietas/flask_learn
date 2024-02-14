from datetime import timedelta
from flask import Flask, session

from .extensions import db, migrate,ma
from .route.user import user
from .route.std import std
from flask_jwt_extended import JWTManager
import os
from dotenv import load_dotenv


def create_app():
    load_dotenv()
    app = Flask(__name__)
    """Put these config code inside a file inside config file and import the config object"""
    # app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=240)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    # app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER')
    
    jwt = JWTManager(app)
    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)

    app.register_blueprint(user)
    # app.register_blueprint(user,url_prefix="/user")
    # app.register_blueprint(std)

    return app
