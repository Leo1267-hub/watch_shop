import sqlite3
from pathlib import Path

from werkzeug.security import generate_password_hash

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "app.db"

def read_image(filename):
    image_path = BASE_DIR / "static" / "demo_watches" / filename
    with open(image_path, "rb") as file:
        return file.read()


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

    watches = [
        ("demo_seller", "Seiko", 220.0, 40.0, "Steel", 145.0, "Automatic everyday watch", 5, read_image("seiko.jpg")),
        ("demo_seller", "Fosil", 75.0, 38.0, "Steel", 55.0, "Nice looking watch", 8, read_image("fosil3.jpg")),
        ("demo_seller", "Tissot", 480.0, 42.0, "Steel", 160.0, "Swiss dress watch", 3, read_image("tissot.jpg")),
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
