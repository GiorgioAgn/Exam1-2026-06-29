DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL,
    languages TEXT
);

DROP TABLE IF EXISTS tours;
CREATE TABLE tours (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guide_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    meeting_point TEXT NOT NULL,
    duration_mins INTEGER NOT NULL,
    language TEXT NOT NULL,
    max_partecipants INTEGER NOT NULL,
    description TEXT NOT NULL,
    stops TEXT NOT NULL,
    photo1 TEXT,
    FOREIGN KEY (guide_id) REFERENCES users (id)
);

DROP TABLE IF EXISTS reservations;
CREATE TABLE reservations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    tour_id INTEGER NOT NULL,
    tour_date TEXT NOT NULL,
    num_people INTEGER NOT NULL,
    extra_names TEXT,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (tour_id) REFERENCES tours (id)
);

DROP TABLE IF EXISTS comments;
CREATE TABLE comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    publication_date TEXT NOT NULL,
    text TEXT NOT NULL,
    post_id INTEGER NOT NULL,
    user_id INTEGER,
    rating INTEGER NOT NULL,
    comment_image TEXT,
    FOREIGN KEY (post_id) REFERENCES tours (id),
    FOREIGN KEY (user_id) REFERENCES users (id)
);