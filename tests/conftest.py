import os
import sqlite3
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture
def app(tmp_path, monkeypatch):
    test_db = tmp_path / "test_app.db"
    schema_path = PROJECT_ROOT / "schema.sql"

    monkeypatch.setenv("DATABASE", str(test_db))
    monkeypatch.setenv("SECRET_KEY", "test-secret-key")

    connection = sqlite3.connect(test_db)
    with open(schema_path, "r", encoding="utf-8") as schema_file:
        connection.executescript(schema_file.read())
    connection.commit()
    connection.close()

    from main import app as flask_app

    flask_app.config.update(
        TESTING=True,
        WTF_CSRF_ENABLED=False,
        SESSION_TYPE="filesystem",
    )

    yield flask_app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db_path(tmp_path):
    return tmp_path / "test_app.db"
