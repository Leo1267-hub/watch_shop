import sqlite3
from pathlib import Path

from werkzeug.security import generate_password_hash

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "app.db"


def seed_db():
    if not DATABASE.exists():
        raise FileNotFoundError("app.db was not found. Run python init_db.py first.")

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute(
        "INSERT OR IGNORE INTO seller (user_id, password, income) VALUES (?, ?, ?)",
        ("demo_seller", generate_password_hash("password123"), 0),
    )
    cursor.execute(
        "INSERT OR IGNORE INTO buyer (user_id, password, budget) VALUES (?, ?, ?)",
        ("demo_buyer", generate_password_hash("password123"), 2500),
    )

    demo_image = b""
    watches = [
        ("demo_seller", "Seiko", 220.0, 40.0, "Steel", 145.0, "Automatic everyday watch", 5, demo_image),
        ("demo_seller", "Casio", 75.0, 38.0, "Resin", 55.0, "Digital retro watch", 8, demo_image),
        ("demo_seller", "Tissot", 480.0, 42.0, "Steel", 160.0, "Swiss dress watch", 3, demo_image),
    ]

    cursor.executemany(
        """INSERT INTO watches
           (user_id, title, price, size, material, weight, description, quantity, watch_picture)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        watches,
    )

    cursor.execute(
        """INSERT INTO reviews (seller_id, buyer_id, review, date)
           VALUES (?, ?, ?, ?)""",
        ("demo_seller", "demo_buyer", "Great seller and fast service.", "2026-06-02 18:37:27"),
    )

    cursor.execute(
        """INSERT INTO messages_to_response_buyer (buyer_id, message, date)
           VALUES (?, ?, ?)""",
        ("demo_buyer", "Can I return a watch after purchase?", "2026-06-02 18:37:27"),
    )

    connection.commit()
    connection.close()
    print("Demo data inserted successfully.")


if __name__ == "__main__":
    seed_db()
