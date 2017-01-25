import eventlet, logging, time, datetime
from logging.handlers import RotatingFileHandler, SMTPHandler
from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from reverse_proxied import ReverseProxied

CONFIGURATION_FILE = "flaskconfig.py"

# Allow server-side session
session = Session()
db = SQLAlchemy()

def create_application(__package_name__):
    app = Flask(__package_name__)
    app.config.from_pyfile(CONFIGURATION_FILE, silent=True)
    # app.secret_key = app.config["SECRET_KEY"]
    app.wsgi_app = ReverseProxied(app.wsgi_app)

    # Initialization
    initialize_plugins(app, __package_name__)
    initialize_logger(app, __package_name__)

    # Register blueprints
    from blueprints import home
    app.register_blueprint(home.node, url_prefix="/home")

    return app

def initialize_plugins(app, __package_name__):
    # Initializing Flask plugins here
    session.init_app(app)
    db.init_app(app)

def initialize_logger(app, __package_name__):
    # Push logging to gunicorn
    if __package_name__ == "__main__": # Debug mode
        app.logger.addHandler(logging.StreamHandler())
    else: # Production mode
        # DEBUG
        log_handler = RotatingFileHandler(filename=app.config["DEBUG_LOG_FILE"], maxBytes=1048576, backupCount=50)
        log_handler.setFormatter(logging.Formatter(app.config["LOG_FORMAT"]))
        log_handler.setLevel(logging.DEBUG)
        app.logger.addHandler(log_handler)
        # INFO
        log_handler = RotatingFileHandler(filename=app.config["INFO_LOG_FILE"], maxBytes=1048576, backupCount=50)
        log_handler.setFormatter(logging.Formatter("[%(levelname)s](%(asctime)s): %(message)s"))
        log_handler.setLevel(logging.INFO)
        app.logger.addHandler(log_handler)
        # ERROR
        log_handler = RotatingFileHandler(filename=app.config["ERROR_LOG_FILE"], maxBytes=1048576, backupCount=50)
        log_handler.setFormatter(logging.Formatter(app.config["LOG_FORMAT"]))
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
