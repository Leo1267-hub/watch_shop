from flask import g
import os
import sqlite3

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_DATABASE = os.path.join(BASE_DIR, "app.db")


def get_database_path():
    return os.environ.get("DATABASE", DEFAULT_DATABASE)


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(get_database_path())
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()
