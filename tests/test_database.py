import sqlite3


def test_schema_creates_required_tables(tmp_path):
    db_path = tmp_path / "schema_test.db"

    connection = sqlite3.connect(db_path)
    with open("schema.sql", "r", encoding="utf-8") as schema_file:
        connection.executescript(schema_file.read())

    tables = {
        row[0]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        ).fetchall()
    }

    connection.close()

    expected_tables = {
        "buyer",
        "seller",
        "watches",
        "watches_to_check",
        "favourite",
        "selling_history",
        "reviews",
        "messages_to_response_buyer",
        "responded_messages_buyer",
        "blocked_sellers",
    }

    assert expected_tables.issubset(tables)


def test_watches_table_accepts_basic_watch(tmp_path):
    db_path = tmp_path / "watch_insert_test.db"

    connection = sqlite3.connect(db_path)
    with open("schema.sql", "r", encoding="utf-8") as schema_file:
        connection.executescript(schema_file.read())

    connection.execute(
        "INSERT INTO seller (user_id, password, income) VALUES (?, ?, ?)",
        ("seller_test", "hashed-password", 0),
    )
    connection.execute(
        """INSERT INTO watches
           (user_id, title, price, size, material, weight, description, quantity, watch_picture)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        ("seller_test", "Seiko", 220.0, 40.0, "Steel", 145.0, "Demo watch", 5, b""),
    )
    connection.commit()

    watch = connection.execute("SELECT * FROM watches WHERE title = ?", ("Seiko",)).fetchone()
    connection.close()

    assert watch is not None
