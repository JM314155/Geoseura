CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
);

CREATE TABLE items (
    id INTEGER PRIMARY KEY,
    title TEXT,
    description TEXT,
    coordinates TEXT,
    created_date TEXT,
    user_id INTEGER REFERENCES users(id)
);

CREATE TABLE visits (
    id INTEGER PRIMARY KEY,
    item_id INTEGER REFERENCES items(id),
    user_id INTEGER REFERENCES users(id),
    visit_date TEXT
);

CREATE TABLE classes (
    id INTEGER PRIMARY KEY,
    title TEXT,
    value TEXT
);

CREATE TABLE item_classes (
    id INTEGER PRIMARY KEY,
    item_id INTEGER REFERENCES items(id),
    title TEXT,
    value TEXT
);

CREATE TABLE images (
    id INTEGER PRIMARY KEY,
    item_id INTEGER REFERENCES items(id),
    image BLOB
);
