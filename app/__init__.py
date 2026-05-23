from flask import Flask
from flask_session import Session

from app.database import close_db
from config import Config


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    Session(app)
    app.teardown_appcontext(close_db)

    return app