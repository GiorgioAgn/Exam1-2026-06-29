PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS tour_reports;
DROP TABLE IF EXISTS tour_likes;
DROP TABLE IF EXISTS comments;
DROP TABLE IF EXISTS reservations;
DROP TABLE IF EXISTS tour_photos;
DROP TABLE IF EXISTS tour_stops;
DROP TABLE IF EXISTS tour_schedule;
DROP TABLE IF EXISTS tours;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('guide', 'participant')),
    languages TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (email, role)
);

CREATE TABLE tours (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guide_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    theme TEXT NOT NULL,
    meeting_point TEXT NOT NULL,
    duration_mins INTEGER NOT NULL CHECK (duration_mins > 0),
    language TEXT NOT NULL,
    max_participants INTEGER NOT NULL CHECK (max_participants > 0),
    description TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (guide_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE tour_schedule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tour_id INTEGER NOT NULL,
    weekday INTEGER NOT NULL CHECK (weekday BETWEEN 0 AND 6),
    start_time TEXT NOT NULL,
    FOREIGN KEY (tour_id) REFERENCES tours (id) ON DELETE CASCADE,
    UNIQUE (tour_id, weekday)
);

CREATE TABLE tour_stops (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tour_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    position INTEGER NOT NULL,
    FOREIGN KEY (tour_id) REFERENCES tours (id) ON DELETE CASCADE
);

CREATE TABLE tour_photos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tour_id INTEGER NOT NULL,
    path TEXT NOT NULL,
    position INTEGER NOT NULL,
    FOREIGN KEY (tour_id) REFERENCES tours (id) ON DELETE CASCADE,
    UNIQUE (tour_id, position)
);

CREATE TABLE reservations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    tour_id INTEGER NOT NULL,
    tour_date TEXT NOT NULL,
    num_people INTEGER NOT NULL CHECK (num_people BETWEEN 1 AND 4),
    extra_names TEXT,
    status TEXT NOT NULL DEFAULT 'booked' CHECK (status IN ('booked', 'cancelled')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    cancelled_at TEXT,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (tour_id) REFERENCES tours (id) ON DELETE CASCADE,
    UNIQUE (user_id, tour_id, tour_date)
);

CREATE TABLE tour_likes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tour_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tour_id) REFERENCES tours (id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    UNIQUE (tour_id, user_id)
);

CREATE TABLE comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tour_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    publication_date TEXT NOT NULL,
    text TEXT NOT NULL,
    FOREIGN KEY (tour_id) REFERENCES tours (id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE tour_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tour_id INTEGER NOT NULL,
    tour_date TEXT NOT NULL,
    actual_participants INTEGER NOT NULL CHECK (actual_participants >= 0),
    evidence_photo TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tour_id) REFERENCES tours (id) ON DELETE CASCADE,
    UNIQUE (tour_id, tour_date)
);
