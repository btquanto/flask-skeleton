# -*- coding: utf-8 -*-
# Libraries
import datetime, eventlet, logging, time
from logging.handlers import (
    RotatingFileHandler,
    SMTPHandler,
)

# Flask plugins
from flask import Flask
from flask_login import LoginManager
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy

# App modules
from .access import RBAC

# Constants
CONFIGURATION_FILE = "flaskconfig.py"

# Allow server-side session
db = SQLAlchemy()
login_manager = LoginManager()
session = Session()
rbac = RBAC()

def create_application(__package_name__):
    from .reverse_proxied import ReverseProxied
    app = Flask(__package_name__)
    app.config.from_pyfile(CONFIGURATION_FILE, silent=True)
    app.wsgi_app = ReverseProxied(app.wsgi_app)

    # Initialization
    initialize_plugins(app)
    initialize_logger(app, __package_name__)

    # Register blueprints
    from blueprints import home
    app.register_blueprint(home.node, url_prefix="/home")

    return app

def initialize_plugins(app):
    # Initializing Flask plugins here

    # SQLAlchemy
    db.init_app(app)

    # Flask-Login
    from .access import load_user
    login_manager.init_app(app)
    login_manager.user_loader(load_user)

    # RBAC
    from models import User, Role
    rbac.init_app(app)
    rbac.role_model(Role)
    rbac.user_model(User)

    # Flask-Session
    session.init_app(app)

def initialize_logger(app, __package_name__):
    if __package_name__ == "__main__": # Debug mode
        app.logger.addHandler(logging.StreamHandler())
    else: # Production mode
        # INFO
        log_handler = RotatingFileHandler(filename=app.config["INFO_LOG_FILE"],
                                            maxBytes=app.config['MAX_LOG_FILE_SIZE'],
                                            backupCount=app.config['LOG_BACKUP_COUNT'])
        log_handler.setFormatter(logging.Formatter(app.config["LOG_FORMAT_INFO"]))
        log_handler.setLevel(logging.INFO)
        app.logger.addHandler(log_handler)

        # DEBUG
        log_handler = RotatingFileHandler(filename=app.config["DEBUG_LOG_FILE"],
                                            maxBytes=app.config['MAX_LOG_FILE_SIZE'],
                                            backupCount=app.config['LOG_BACKUP_COUNT'])
        log_handler.setFormatter(logging.Formatter(app.config["LOG_FORMAT_DEBUG"]))
        log_handler.setLevel(logging.DEBUG)
        app.logger.addHandler(log_handler)

        # ERROR
        log_handler = RotatingFileHandler(filename=app.config["ERROR_LOG_FILE"],
                                            maxBytes=app.config['MAX_LOG_FILE_SIZE'],
                                            backupCount=app.config['LOG_BACKUP_COUNT'])
        log_handler.setFormatter(logging.Formatter(app.config["LOG_FORMAT_ERROR"]))
        log_handler.setLevel(logging.ERROR)
        app.logger.addHandler(log_handler)

        # Send errors to admin emails
        mail_handler = SMTPHandler("127.0.0.1",
                                   app.config["ERROR_REPORT_FROM_EMAIL"],
                                   app.config["ERROR_REPORT_TO_EMAILS"],
                                   app.config["ERROR_REPORT_TITLE"])
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

    app.logger.setLevel(logging.DEBUG)
