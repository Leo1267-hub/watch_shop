DROP TABLE IF EXISTS seller;

CREATE TABLE seller
( 
    user_id TEXT PRIMARY KEY,
    password TEXT NOT NULL,
    income REAL NOT NULL DEFAULT 0
);

DROP TABLE IF EXISTS buyer;

CREATE TABLE buyer
( 
    user_id TEXT PRIMARY KEY,
    password TEXT NOT NULL,
    budget REAL NOT NULL DEFAULT 0
);


DROP TABLE IF EXISTS watches;

CREATE TABLE watches
(
    user_id TEXT NOT NULL,
    watch_id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    price REAL NOT NULL,
    size REAL NOT NULL,
    material NOT NULL,
    weight NOT NULL,
    description TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    watch_picture blob,
    FOREIGN KEY(user_id) REFERENCES seller(user_id)
);

DROP TABLE IF EXISTS watches_to_check;

CREATE TABLE watches_to_check
(
    user_id TEXT NOT NULL,
    watch_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    price REAL NOT NULL,
    size REAL NOT NULL,
    material NOT NULL,
    weight NOT NULL,
    description TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    watch_picture blob,
    FOREIGN KEY(user_id) REFERENCES seller(user_id)
);

DROP TABLE IF EXISTS favourite;

CREATE TABLE favourite
(
    user_id TEXT NOT NULL,
    watch_id TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES buyer(user_id),
    FOREIGN KEY(watch_id) REFERENCES watches(watch_id)
);


DROP TABLE IF EXISTS selling_history;

CREATE TABLE selling_history
(
    user_id TEXT NOT NULL,
    buyer_id TEXT,
    watch_id INTEGER,
    title TEXT NOT NULL,
    price REAL NOT NULL,
    size REAL NOT NULL,
    material NOT NULL,
    weight NOT NULL,
    description TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    watch_picture blob,
    date TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES seller(user_id),
    FOREIGN KEY(watch_id) REFERENCES watches(watch_id),
    FOREIGN KEY(buyer_id) REFERENCES buyer(user_id)
);

DROP TABLE IF EXISTS reviews;

CREATE TABLE reviews
(
    seller_id TEXT NOT NULL,
    buyer_id TEXT NOT NULL,
    review TEXT NOT NULL,
    review_id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    FOREIGN KEY(seller_id) REFERENCES seller(user_id),
    FOREIGN KEY(buyer_id) REFERENCES buyer(user_id)
);


DROP TABLE IF EXISTS messages_to_response_buyer;

CREATE TABLE messages_to_response_buyer
(
    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
    buyer_id TEXT NOT NULL,
    message TEXT NOT NULL,
    date TEXT NOT NULL,
    FOREIGN KEY(buyer_id) REFERENCES seller(buyer_id)
);

DROP TABLE IF EXISTS responded_messages_buyer;

CREATE TABLE responded_messages_buyer
(
    message_id INTEGER PRIMARY KEY,
    buyer_id TEXT NOT NULL,
    last_message TEXT NOT NULL,
    last_date TEXT NOT NULL,
    message TEXT NOT NULL,
    date TEXT NOT NULL,
    FOREIGN KEY(buyer_id) REFERENCES buyer(buyer_id)
);

DROP TABLE IF EXISTS blocked_sellers;

CREATE TABLE blocked_sellers
(
    buyer_id TEXT NOT NULL,
    seller_id TEXT NOT NULL,
    FOREIGN KEY(buyer_id) REFERENCES buyer(buyer_id),
    FOREIGN KEY(seller_id) REFERENCES seller(seller_id)
);