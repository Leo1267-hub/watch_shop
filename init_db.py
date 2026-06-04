import os
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "app.db"
SCHEMA = BASE_DIR / "schema.sql"


def init_db():
    if not SCHEMA.exists():
        raise FileNotFoundError("schema.sql was not found")

    if DATABASE.exists():
        DATABASE.unlink()

    connection = sqlite3.connect(DATABASE)
    with open(SCHEMA, "r", encoding="utf-8") as schema_file:
        connection.executescript(schema_file.read())
    connection.commit()
    connection.close()
    print("Database created successfully: app.db")


if __name__ == "__main__":
    init_db()
