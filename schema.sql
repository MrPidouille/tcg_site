DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS cards;
DROP TABLE IF EXISTS user_cards;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    is_admin BOOLEAN DEFAULT 0
);

CREATE TABLE cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    edition TEXT NOT NULL,
    rarity TEXT NOT NULL,
    price INTEGER NOT NULL
);

CREATE TABLE user_cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    card_id INTEGER,
    quantity INTEGER DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (card_id) REFERENCES cards(id)
);