import os
import hashlib
import sqlite3


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "database.db")
SAMPLE_SALT = "siracusa-sample"
SAMPLE_ITERATIONS = 1000000


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def make_password_hash(password):
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        SAMPLE_SALT.encode("utf-8"),
        SAMPLE_ITERATIONS,
    ).hex()
    return f"pbkdf2:sha256:{SAMPLE_ITERATIONS}${SAMPLE_SALT}${digest}"


def insert_user(conn, first_name, last_name, email, password, role, languages=""):
    cursor = conn.execute(
        """
        INSERT INTO users (first_name, last_name, email, password, role, languages)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            first_name,
            last_name,
            email,
            make_password_hash(password),
            role,
            languages,
        ),
    )
    return cursor.lastrowid


def insert_tour(conn, guide_id, title, theme, meeting_point, duration, language, max_people, description, schedules, stops, photos):
    cursor = conn.execute(
        """
        INSERT INTO tours
            (guide_id, title, theme, meeting_point, duration_mins, language, max_participants, description)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (guide_id, title, theme, meeting_point, duration, language, max_people, description),
    )
    tour_id = cursor.lastrowid

    for weekday, start_time in schedules:
        conn.execute(
            "INSERT INTO tour_schedule (tour_id, weekday, start_time) VALUES (?, ?, ?)",
            (tour_id, weekday, start_time),
        )
    for position, stop in enumerate(stops, start=1):
        conn.execute(
            "INSERT INTO tour_stops (tour_id, name, position) VALUES (?, ?, ?)",
            (tour_id, stop, position),
        )
    for position, photo in enumerate(photos, start=1):
        conn.execute(
            "INSERT INTO tour_photos (tour_id, path, position) VALUES (?, ?, ?)",
            (tour_id, photo, position),
        )
    return tour_id


def seed_sample_data(conn):
    password = "password123"
    guide_lucia = insert_user(
        conn,
        "Lucia",
        "Amenta",
        "lucia@siracusawalks.test",
        password,
        "guide",
        "Italian,English,Spanish",
    )
    guide_marco = insert_user(
        conn,
        "Marco",
        "Greco",
        "marco@siracusawalks.test",
        password,
        "guide",
        "Italian,German,Portuguese",
    )
    participant_anna = insert_user(
        conn,
        "Anna",
        "Ferraro",
        "anna@example.test",
        password,
        "participant",
    )
    participant_paolo = insert_user(
        conn,
        "Paolo",
        "Rizzo",
        "paolo@example.test",
        password,
        "participant",
    )
    participant_lucia = insert_user(
        conn,
        "Lucia",
        "Amenta",
        "lucia@siracusawalks.test",
        password,
        "participant",
    )

    photos = [
        "/static/assets/img/category-hiking.jpg",
        "/static/assets/img/category-trekking.jpg",
        "/static/assets/img/category-orienteering.jpg",
        "/static/assets/img/trail-forest.jpg",
        "/static/assets/img/trail-ridge.jpg",
    ]
    second_photos = [
        "/static/assets/img/trail-lake.jpg",
        "/static/assets/img/category-rafting.jpg",
        "/static/assets/img/category-kayak.jpg",
        "/static/assets/img/category-zipline.jpg",
        "/static/assets/img/trail-forest.jpg",
    ]

    ortigia = insert_tour(
        conn,
        guide_lucia,
        "Ortigia al tramonto",
        "Storia e leggende",
        "Fontana di Diana, Piazza Archimede",
        120,
        "Italian",
        12,
        "Una passeggiata serale tra vicoli, cortili e affacci sul mare per scoprire le storie piu note e quelle piu nascoste di Ortigia.",
        [(0, "18:00"), (2, "18:00"), (5, "18:30")],
        ["Piazza Archimede", "Duomo di Siracusa", "Fonte Aretusa", "Lungomare Alfeo"],
        photos,
    )
    neapolis = insert_tour(
        conn,
        guide_lucia,
        "Greek myths in Neapolis",
        "Archeologia",
        "Ingresso Parco Archeologico della Neapolis",
        150,
        "English",
        10,
        "A slow walk through Greek theatre stories, ancient quarries and the myths that shaped the cultural identity of Syracuse.",
        [(1, "09:30"), (3, "09:30")],
        ["Greek Theatre", "Latomia del Paradiso", "Ear of Dionysius", "Roman Amphitheatre"],
        second_photos,
    )
    street_food = insert_tour(
        conn,
        guide_marco,
        "Sapori e mercati di Siracusa",
        "Gastronomia",
        "Tempio di Apollo",
        100,
        "Italian",
        8,
        "Un itinerario conviviale tra botteghe, mercato storico e racconti di cucina locale, pensato per conoscere Siracusa attraverso i suoi sapori.",
        [(4, "19:00"), (6, "11:00")],
        ["Tempio di Apollo", "Mercato di Ortigia", "Via Cavour", "Marina"],
        photos,
    )
    mare = insert_tour(
        conn,
        guide_marco,
        "Meerblick und Barock",
        "Architettura",
        "Porta Marina",
        90,
        "German",
        6,
        "Eine kompakte Tour auf Deutsch zwischen barocken Fassaden, Meerblicken und den kleinen Plaetzen der Altstadt von Siracusa.",
        [(5, "10:00")],
        ["Porta Marina", "Piazza Duomo", "Palazzo Beneventano", "Belvedere San Giacomo"],
        second_photos,
    )

    conn.execute(
        """
        INSERT INTO reservations (user_id, tour_id, tour_date, num_people, extra_names)
        VALUES (?, ?, ?, ?, ?)
        """,
        (participant_anna, ortigia, "2026-07-06", 2, "Marta Ferraro"),
    )
    conn.execute(
        """
        INSERT INTO reservations (user_id, tour_id, tour_date, num_people, extra_names)
        VALUES (?, ?, ?, ?, ?)
        """,
        (participant_paolo, neapolis, "2026-07-07", 1, ""),
    )
    conn.execute(
        """
        INSERT INTO reservations (user_id, tour_id, tour_date, num_people, extra_names)
        VALUES (?, ?, ?, ?, ?)
        """,
        (participant_lucia, street_food, "2026-07-05", 3, "Nico Amenta, Sara Leone"),
    )
    conn.execute(
        """
        INSERT INTO reservations (user_id, tour_id, tour_date, num_people, extra_names)
        VALUES (?, ?, ?, ?, ?)
        """,
        (participant_anna, street_food, "2026-06-07", 2, "Marta Ferraro"),
    )
    conn.execute(
        """
        INSERT INTO comments (tour_id, user_id, publication_date, text)
        VALUES (?, ?, ?, ?)
        """,
        (ortigia, guide_lucia, "2026-06-10", "Portate scarpe comode: il giro resta leggero, ma alcune strade sono in pietra."),
    )
    conn.execute(
        """
        INSERT INTO comments (tour_id, user_id, publication_date, text)
        VALUES (?, ?, ?, ?)
        """,
        (ortigia, participant_anna, "2026-06-11", "Bellissima idea per scoprire Ortigia con calma. Ho prenotato per luglio!"),
    )
    conn.execute(
        """
        INSERT INTO tour_reports (tour_id, tour_date, actual_participants, evidence_photo)
        VALUES (?, ?, ?, ?)
        """,
        (street_food, "2026-06-07", 2, "/static/assets/img/category-hiking.jpg"),
    )


def init_db():
    conn = get_db_connection()
    with open(os.path.join(BASE_DIR, "schema.sql"), "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    seed_sample_data(conn)
    conn.commit()
    conn.close()
    print("Database inizializzato con dati campione.")


if __name__ == "__main__":
    init_db()
