import datetime as dt
import os
import uuid

from flask import Flask, abort, flash, redirect, render_template, request, url_for
from flask_login import LoginManager, UserMixin, current_user, login_required, login_user, logout_user
from sqlite3 import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from db import get_db_connection


app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "super_chiave_segreta_esame")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
LANGUAGES = ["Italian", "English", "Spanish", "Portuguese", "German"]
WEEKDAYS = [
    (0, "Lunedi"),
    (1, "Martedi"),
    (2, "Mercoledi"),
    (3, "Giovedi"),
    (4, "Venerdi"),
    (5, "Sabato"),
    (6, "Domenica"),
]
WEEKDAY_NAMES = dict(WEEKDAYS)
DURATION_FILTERS = {
    "short": ("Fino a 90 min", 0, 90),
    "medium": ("91-150 min", 91, 150),
    "long": ("Oltre 150 min", 151, 10000),
}

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


class User(UserMixin):
    def __init__(self, id, email, role, first_name, last_name, languages=""):
        self.id = id
        self.email = email
        self.role = role
        self.first_name = first_name
        self.last_name = last_name
        self.languages = languages or ""

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def spoken_languages(self):
        return [lang.strip() for lang in self.languages.split(",") if lang.strip()]


@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    user_row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    if user_row:
        return User(
            user_row["id"],
            user_row["email"],
            user_row["role"],
            user_row["first_name"],
            user_row["last_name"],
            user_row["languages"],
        )
    return None


@app.context_processor
def inject_constants():
    return {
        "LANGUAGES": LANGUAGES,
        "WEEKDAYS": WEEKDAYS,
        "WEEKDAY_NAMES": WEEKDAY_NAMES,
        "DURATION_FILTERS": DURATION_FILTERS,
    }


def normalize_email(email):
    return (email or "").strip().lower()


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_file(file):
    return file and file.filename and allowed_file(file.filename)


def save_uploaded_file(file, prefix):
    if not validate_file(file):
        raise ValueError("File non valido. Usa png, jpg, jpeg, gif oppure webp.")
    original = secure_filename(file.filename)
    ext = original.rsplit(".", 1)[1].lower()
    filename = f"{prefix}-{uuid.uuid4().hex}.{ext}"
    file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
    return f"/static/uploads/{filename}"


def parse_positive_int(value, label, min_value=1, max_value=None):
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        raise ValueError(f"{label} deve essere un numero.")
    if parsed < min_value:
        raise ValueError(f"{label} deve essere almeno {min_value}.")
    if max_value is not None and parsed > max_value:
        raise ValueError(f"{label} non puo superare {max_value}.")
    return parsed


def parse_time_to_minutes(value):
    try:
        parsed = dt.time.fromisoformat(value)
    except (TypeError, ValueError):
        raise ValueError("Orario non valido.")
    return parsed.hour * 60 + parsed.minute


def ranges_overlap(start_a, duration_a, start_b, duration_b):
    end_a = start_a + duration_a
    end_b = start_b + duration_b
    return start_a < end_b and start_b < end_a


def parse_iso_date(value):
    try:
        return dt.date.fromisoformat(value)
    except (TypeError, ValueError):
        raise ValueError("Data non valida.")


def tour_datetime(tour_date, start_time):
    return dt.datetime.combine(tour_date, dt.time.fromisoformat(start_time))


def split_names(value):
    raw = (value or "").replace("\n", ",")
    return [name.strip() for name in raw.split(",") if name.strip()]


def safe_redirect(default_endpoint="index"):
    next_url = request.args.get("next") or request.form.get("next")
    if next_url and next_url.startswith("/") and not next_url.startswith("//"):
        return redirect(next_url)
    return redirect(url_for(default_endpoint))


def require_role(role):
    if not current_user.is_authenticated:
        return redirect(url_for("login", next=request.path))
    if current_user.role != role:
        flash("Questo account non ha i permessi per eseguire questa azione.", "warning")
        return redirect(url_for("index"))
    return None


def get_schedules(conn, tour_id):
    return conn.execute(
        "SELECT * FROM tour_schedule WHERE tour_id = ? ORDER BY weekday",
        (tour_id,),
    ).fetchall()


def get_schedule_for_date(conn, tour_id, tour_date):
    return conn.execute(
        """
        SELECT * FROM tour_schedule
        WHERE tour_id = ? AND weekday = ?
        """,
        (tour_id, tour_date.weekday()),
    ).fetchone()


def format_schedule(schedules):
    return ", ".join(f"{WEEKDAY_NAMES[row['weekday']]} {row['start_time']}" for row in schedules)


def get_stops(conn, tour_id):
    return conn.execute(
        "SELECT * FROM tour_stops WHERE tour_id = ? ORDER BY position",
        (tour_id,),
    ).fetchall()


def get_photos(conn, tour_id):
    return conn.execute(
        "SELECT * FROM tour_photos WHERE tour_id = ? ORDER BY position",
        (tour_id,),
    ).fetchall()


def primary_photo(conn, tour_id):
    photo = conn.execute(
        "SELECT path FROM tour_photos WHERE tour_id = ? ORDER BY position LIMIT 1",
        (tour_id,),
    ).fetchone()
    return photo["path"] if photo else "/static/assets/img/trail-forest.jpg"


def get_tour_row(conn, tour_id):
    return conn.execute(
        """
        SELECT tours.*, users.first_name AS guide_first_name,
               users.last_name AS guide_last_name, users.email AS guide_email,
               users.languages AS guide_languages
        FROM tours
        JOIN users ON users.id = tours.guide_id
        WHERE tours.id = ?
        """,
        (tour_id,),
    ).fetchone()


def active_reserved_places(conn, tour_id, tour_date):
    row = conn.execute(
        """
        SELECT COALESCE(SUM(num_people), 0) AS total
        FROM reservations
        WHERE tour_id = ? AND tour_date = ? AND status = 'booked'
        """,
        (tour_id, tour_date.isoformat()),
    ).fetchone()
    return row["total"]


def available_places(conn, tour, tour_date):
    return tour["max_participants"] - active_reserved_places(conn, tour["id"], tour_date)


def tour_has_any_reservations(conn, tour_id):
    row = conn.execute(
        "SELECT COUNT(*) AS total FROM reservations WHERE tour_id = ?",
        (tour_id,),
    ).fetchone()
    return row["total"] > 0


def guide_has_overlap(conn, guide_id, weekday, start_time, duration_mins, exclude_tour_id=None):
    sql = """
        SELECT tours.id, tours.title, tours.duration_mins, tour_schedule.start_time
        FROM tours
        JOIN tour_schedule ON tour_schedule.tour_id = tours.id
        WHERE tours.guide_id = ? AND tour_schedule.weekday = ?
    """
    params = [guide_id, weekday]
    if exclude_tour_id is not None:
        sql += " AND tours.id <> ?"
        params.append(exclude_tour_id)

    start_minutes = parse_time_to_minutes(start_time)
    for row in conn.execute(sql, params).fetchall():
        other_start = parse_time_to_minutes(row["start_time"])
        if ranges_overlap(start_minutes, duration_mins, other_start, row["duration_mins"]):
            return row
    return None


def participant_has_overlap(conn, user_id, tour_date, start_time, duration_mins):
    rows = conn.execute(
        """
        SELECT reservations.id, tours.title, tours.duration_mins, tour_schedule.start_time
        FROM reservations
        JOIN tours ON tours.id = reservations.tour_id
        JOIN tour_schedule
             ON tour_schedule.tour_id = tours.id
            AND tour_schedule.weekday = ?
        WHERE reservations.user_id = ?
          AND reservations.tour_date = ?
          AND reservations.status = 'booked'
        """,
        (tour_date.weekday(), user_id, tour_date.isoformat()),
    ).fetchall()
    start_minutes = parse_time_to_minutes(start_time)
    for row in rows:
        other_start = parse_time_to_minutes(row["start_time"])
        if ranges_overlap(start_minutes, duration_mins, other_start, row["duration_mins"]):
            return row
    return None


def upcoming_dates(conn, tour, horizon_days=60):
    today = dt.date.today()
    now = dt.datetime.now()
    schedules = {row["weekday"]: row for row in get_schedules(conn, tour["id"])}
    dates = []
    for offset in range(horizon_days + 1):
        candidate = today + dt.timedelta(days=offset)
        schedule = schedules.get(candidate.weekday())
        if not schedule:
            continue
        start_dt = tour_datetime(candidate, schedule["start_time"])
        if start_dt <= now:
            continue
        seats_left = available_places(conn, tour, candidate)
        dates.append(
            {
                "date": candidate,
                "date_iso": candidate.isoformat(),
                "weekday": WEEKDAY_NAMES[candidate.weekday()],
                "start_time": schedule["start_time"],
                "seats_left": seats_left,
            }
        )
    return dates


def enrich_tour(conn, row, selected_date=None):
    tour = dict(row)
    tour["schedule"] = get_schedules(conn, tour["id"])
    tour["schedule_label"] = format_schedule(tour["schedule"])
    tour["primary_photo"] = primary_photo(conn, tour["id"])
    tour["can_edit"] = not tour_has_any_reservations(conn, tour["id"])
    if selected_date:
        schedule = get_schedule_for_date(conn, tour["id"], selected_date)
        tour["selected_start_time"] = schedule["start_time"] if schedule else None
        tour["selected_seats_left"] = available_places(conn, tour, selected_date) if schedule else None
    return tour


def filtered_tours(conn, filters):
    rows = conn.execute(
        """
        SELECT tours.*, users.first_name AS guide_first_name,
               users.last_name AS guide_last_name
        FROM tours
        JOIN users ON users.id = tours.guide_id
        ORDER BY tours.created_at DESC, tours.id DESC
        """
    ).fetchall()

    selected_date = None
    if filters.get("date"):
        selected_date = parse_iso_date(filters["date"])

    results = []
    for row in rows:
        tour = enrich_tour(conn, row, selected_date)
        q = (filters.get("q") or "").strip().lower()
        if q and q not in tour["title"].lower() and q not in tour["theme"].lower():
            continue
        if filters.get("language") and tour["language"] != filters["language"]:
            continue
        duration_key = filters.get("duration")
        if duration_key:
            _, min_duration, max_duration = DURATION_FILTERS[duration_key]
            if not (min_duration <= tour["duration_mins"] <= max_duration):
                continue
        if selected_date and not get_schedule_for_date(conn, tour["id"], selected_date):
            continue
        results.append(tour)
    return results


def parse_schedule_form():
    schedules = []
    errors = []
    for weekday, label in WEEKDAYS:
        if request.form.get(f"day_{weekday}"):
            start_time = (request.form.get(f"time_{weekday}") or "").strip()
            if not start_time:
                errors.append(f"Inserisci un orario per {label}.")
                continue
            try:
                parse_time_to_minutes(start_time)
            except ValueError:
                errors.append(f"Orario non valido per {label}.")
                continue
            schedules.append({"weekday": weekday, "start_time": start_time})
    if not schedules:
        errors.append("Seleziona almeno un giorno della settimana.")
    return schedules, errors


def parse_tour_form(conn, exclude_tour_id=None):
    errors = []
    title = (request.form.get("title") or "").strip()
    theme = (request.form.get("theme") or "").strip()
    meeting_point = (request.form.get("meeting_point") or "").strip()
    description = (request.form.get("description") or "").strip()
    language = (request.form.get("language") or "").strip()
    stops = split_names(request.form.get("stops"))

    if len(title) < 4:
        errors.append("Il titolo deve contenere almeno 4 caratteri.")
    if len(theme) < 3:
        errors.append("Inserisci un tema del tour.")
    if len(meeting_point) < 4:
        errors.append("Inserisci un punto di ritrovo chiaro.")
    if len(description) < 30:
        errors.append("La descrizione deve contenere almeno 30 caratteri.")
    if language not in current_user.spoken_languages:
        errors.append("La lingua del tour deve essere tra quelle parlate dalla guida.")
    if not stops:
        errors.append("Inserisci almeno una tappa.")

    try:
        duration_mins = parse_positive_int(request.form.get("duration_mins"), "Durata", 30, 360)
    except ValueError as exc:
        duration_mins = None
        errors.append(str(exc))

    try:
        max_participants = parse_positive_int(
            request.form.get("max_participants"),
            "Numero massimo di partecipanti",
            1,
            40,
        )
    except ValueError as exc:
        max_participants = None
        errors.append(str(exc))

    schedules, schedule_errors = parse_schedule_form()
    errors.extend(schedule_errors)

    if duration_mins:
        for schedule in schedules:
            overlap = guide_has_overlap(
                conn,
                current_user.id,
                schedule["weekday"],
                schedule["start_time"],
                duration_mins,
                exclude_tour_id,
            )
            if overlap:
                errors.append(
                    f"Sovrapposizione agenda: {WEEKDAY_NAMES[schedule['weekday']]} "
                    f"{schedule['start_time']} coincide con '{overlap['title']}'."
                )

    return {
        "title": title,
        "theme": theme,
        "meeting_point": meeting_point,
        "duration_mins": duration_mins,
        "language": language,
        "max_participants": max_participants,
        "description": description,
        "stops": stops,
        "schedules": schedules,
    }, errors


def get_form_photo_files():
    return [request.files.get(f"photo{i}") for i in range(1, 6)]


def validate_five_photos(files, required):
    provided = [file for file in files if file and file.filename]
    if required and len(provided) != 5:
        return "Devi caricare esattamente 5 foto promozionali."
    if not required and provided and len(provided) != 5:
        return "Per sostituire le foto devi caricarne esattamente 5."
    for file in provided:
        if not validate_file(file):
            return "Le foto devono essere png, jpg, jpeg, gif oppure webp."
    return None


def insert_tour_details(conn, tour_id, data, photo_files):
    for schedule in data["schedules"]:
        conn.execute(
            "INSERT INTO tour_schedule (tour_id, weekday, start_time) VALUES (?, ?, ?)",
            (tour_id, schedule["weekday"], schedule["start_time"]),
        )
    for position, stop in enumerate(data["stops"], start=1):
        conn.execute(
            "INSERT INTO tour_stops (tour_id, name, position) VALUES (?, ?, ?)",
            (tour_id, stop, position),
        )
    for position, file in enumerate(photo_files, start=1):
        path = save_uploaded_file(file, f"tour-{tour_id}-{position}")
        conn.execute(
            "INSERT INTO tour_photos (tour_id, path, position) VALUES (?, ?, ?)",
            (tour_id, path, position),
        )


@app.route("/")
def index():
    conn = get_db_connection()
    tours = filtered_tours(conn, {})[:6]
    conn.close()
    return render_template("index.html", tours=tours)


@app.route("/hiking")
@app.route("/tours")
def hiking():
    filters = {
        "q": request.args.get("q", ""),
        "date": request.args.get("date", ""),
        "duration": request.args.get("duration", ""),
        "language": request.args.get("language", ""),
    }
    if filters["duration"] and filters["duration"] not in DURATION_FILTERS:
        filters["duration"] = ""
    if filters["language"] and filters["language"] not in LANGUAGES:
        filters["language"] = ""

    conn = get_db_connection()
    try:
        tours = filtered_tours(conn, filters)
    except ValueError:
        flash("Il filtro data non e valido.", "warning")
        filters["date"] = ""
        tours = filtered_tours(conn, filters)
    conn.close()
    return render_template("hiking.html", tours=tours, filters=filters)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = normalize_email(request.form.get("email"))
        password = request.form.get("password") or ""
        role = request.form.get("role")

        if role not in {"guide", "participant"}:
            flash("Seleziona il tipo di account.", "danger")
            return render_template("login.html")

        conn = get_db_connection()
        user_row = conn.execute(
            "SELECT * FROM users WHERE email = ? AND role = ?",
            (email, role),
        ).fetchone()
        conn.close()

        if user_row and check_password_hash(user_row["password"], password):
            user_obj = User(
                user_row["id"],
                user_row["email"],
                user_row["role"],
                user_row["first_name"],
                user_row["last_name"],
                user_row["languages"],
            )
            login_user(user_obj)
            return safe_redirect()
        flash("Credenziali errate per il tipo di account selezionato.", "danger")
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        first_name = (request.form.get("first_name") or "").strip()
        last_name = (request.form.get("last_name") or "").strip()
        email = normalize_email(request.form.get("email"))
        password = request.form.get("password") or ""
        role = request.form.get("role")
        selected_languages = request.form.getlist("languages")
        errors = []

        if len(first_name) < 2:
            errors.append("Inserisci un nome valido.")
        if len(last_name) < 2:
            errors.append("Inserisci un cognome valido.")
        if "@" not in email or "." not in email:
            errors.append("Inserisci una email valida.")
        if len(password) < 6:
            errors.append("La password deve avere almeno 6 caratteri.")
        if role not in {"guide", "participant"}:
            errors.append("Seleziona un tipo account valido.")

        languages = ""
        if role == "guide":
            valid_languages = [lang for lang in selected_languages if lang in LANGUAGES]
            if not valid_languages:
                errors.append("Una guida deve selezionare almeno una lingua.")
            languages = ",".join(valid_languages)

        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template("register.html")

        conn = get_db_connection()
        try:
            conn.execute(
                """
                INSERT INTO users (first_name, last_name, email, password, role, languages)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    first_name,
                    last_name,
                    email,
                    generate_password_hash(password, method="pbkdf2:sha256"),
                    role,
                    languages,
                ),
            )
            conn.commit()
            flash("Registrazione completata. Ora puoi accedere.", "success")
            return redirect(url_for("login"))
        except IntegrityError:
            flash("Esiste gia un account con questa email e questo ruolo.", "danger")
        finally:
            conn.close()
    return render_template("register.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/create-tour", methods=["GET", "POST"])
@login_required
def create_tour():
    denied = require_role("guide")
    if denied:
        return denied

    if request.method == "POST":
        conn = get_db_connection()
        data, errors = parse_tour_form(conn)
        photo_files = get_form_photo_files()
        photo_error = validate_five_photos(photo_files, required=True)
        if photo_error:
            errors.append(photo_error)

        if errors:
            for error in errors:
                flash(error, "danger")
            conn.close()
            return render_template("create_tour.html", tour=None, selected_schedules={})

        try:
            cursor = conn.execute(
                """
                INSERT INTO tours
                    (guide_id, title, theme, meeting_point, duration_mins,
                     language, max_participants, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    current_user.id,
                    data["title"],
                    data["theme"],
                    data["meeting_point"],
                    data["duration_mins"],
                    data["language"],
                    data["max_participants"],
                    data["description"],
                ),
            )
            tour_id = cursor.lastrowid
            insert_tour_details(conn, tour_id, data, photo_files)
            conn.commit()
            flash("Tour pubblicato con successo.", "success")
            return redirect(url_for("tour_detail", id=tour_id))
        except ValueError as exc:
            conn.rollback()
            flash(str(exc), "danger")
        finally:
            conn.close()

    return render_template("create_tour.html", tour=None, selected_schedules={})


@app.route("/tour/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit_tour(id):
    denied = require_role("guide")
    if denied:
        return denied

    conn = get_db_connection()
    tour = get_tour_row(conn, id)
    if not tour:
        conn.close()
        abort(404)
    if tour["guide_id"] != int(current_user.id):
        conn.close()
        abort(403)
    if tour_has_any_reservations(conn, id):
        conn.close()
        flash("Questo tour ha gia ricevuto prenotazioni e non puo essere modificato.", "warning")
        return redirect(url_for("tour_detail", id=id))

    selected_schedules = {row["weekday"]: row["start_time"] for row in get_schedules(conn, id)}
    stops = ", ".join(row["name"] for row in get_stops(conn, id))
    tour_data = dict(tour)
    tour_data["stops_text"] = stops

    if request.method == "POST":
        data, errors = parse_tour_form(conn, exclude_tour_id=id)
        photo_files = get_form_photo_files()
        provided_files = [file for file in photo_files if file and file.filename]
        photo_error = validate_five_photos(photo_files, required=False)
        if photo_error:
            errors.append(photo_error)

        if errors:
            for error in errors:
                flash(error, "danger")
            conn.close()
            return render_template(
                "create_tour.html",
                tour=tour_data,
                selected_schedules=selected_schedules,
            )

        try:
            conn.execute(
                """
                UPDATE tours
                SET title = ?, theme = ?, meeting_point = ?, duration_mins = ?,
                    language = ?, max_participants = ?, description = ?
                WHERE id = ?
                """,
                (
                    data["title"],
                    data["theme"],
                    data["meeting_point"],
                    data["duration_mins"],
                    data["language"],
                    data["max_participants"],
                    data["description"],
                    id,
                ),
            )
            conn.execute("DELETE FROM tour_schedule WHERE tour_id = ?", (id,))
            conn.execute("DELETE FROM tour_stops WHERE tour_id = ?", (id,))
            for schedule in data["schedules"]:
                conn.execute(
                    "INSERT INTO tour_schedule (tour_id, weekday, start_time) VALUES (?, ?, ?)",
                    (id, schedule["weekday"], schedule["start_time"]),
                )
            for position, stop in enumerate(data["stops"], start=1):
                conn.execute(
                    "INSERT INTO tour_stops (tour_id, name, position) VALUES (?, ?, ?)",
                    (id, stop, position),
                )
            if provided_files:
                conn.execute("DELETE FROM tour_photos WHERE tour_id = ?", (id,))
                for position, file in enumerate(photo_files, start=1):
                    path = save_uploaded_file(file, f"tour-{id}-{position}")
                    conn.execute(
                        "INSERT INTO tour_photos (tour_id, path, position) VALUES (?, ?, ?)",
                        (id, path, position),
                    )
            conn.commit()
            flash("Tour aggiornato.", "success")
            return redirect(url_for("tour_detail", id=id))
        except ValueError as exc:
            conn.rollback()
            flash(str(exc), "danger")
        finally:
            conn.close()
    else:
        conn.close()

    return render_template(
        "create_tour.html",
        tour=tour_data,
        selected_schedules=selected_schedules,
    )


@app.route("/tour/<int:id>")
def tour_detail(id):
    conn = get_db_connection()
    tour_row = get_tour_row(conn, id)
    if not tour_row:
        conn.close()
        abort(404)

    tour = enrich_tour(conn, tour_row)
    stops = get_stops(conn, id)
    photos = get_photos(conn, id)
    dates = upcoming_dates(conn, tour)
    comments = conn.execute(
        """
        SELECT comments.*, users.first_name, users.last_name, users.role
        FROM comments
        JOIN users ON users.id = comments.user_id
        WHERE comments.tour_id = ?
        ORDER BY comments.id DESC
        """,
        (id,),
    ).fetchall()
    conn.close()

    return render_template(
        "tour_detail.html",
        tour=tour,
        stops=stops,
        photos=photos,
        upcoming_dates=dates,
        comments=comments,
    )


@app.route("/tour/<int:id>/book", methods=["POST"])
def book_tour(id):
    if not current_user.is_authenticated:
        flash("Accedi come partecipante per prenotare.", "warning")
        return redirect(url_for("login", next=url_for("tour_detail", id=id)))
    if current_user.role != "participant":
        flash("Le guide non possono prenotare con un account guida.", "warning")
        return redirect(url_for("tour_detail", id=id))

    conn = get_db_connection()
    tour = get_tour_row(conn, id)
    if not tour:
        conn.close()
        abort(404)

    try:
        tour_date = parse_iso_date(request.form.get("tour_date"))
        if tour_date < dt.date.today():
            raise ValueError("Non puoi prenotare una data passata.")
        schedule = get_schedule_for_date(conn, id, tour_date)
        if not schedule:
            raise ValueError("La data scelta non e prevista dallo schedule del tour.")
        if tour_datetime(tour_date, schedule["start_time"]) <= dt.datetime.now():
            raise ValueError("Questo appuntamento e gia iniziato o concluso.")

        num_people = parse_positive_int(request.form.get("num_people"), "Numero partecipanti", 1, 4)
        names = split_names(request.form.get("extra_names"))
        expected_extra = num_people - 1
        if len(names) != expected_extra:
            raise ValueError(
                f"Inserisci esattamente {expected_extra} nome/i aggiuntivo/i per questa prenotazione."
            )
        seats_left = available_places(conn, tour, tour_date)
        if num_people > seats_left:
            raise ValueError(f"Posti insufficienti: ne restano {seats_left}.")

        overlap = participant_has_overlap(
            conn,
            current_user.id,
            tour_date,
            schedule["start_time"],
            tour["duration_mins"],
        )
        if overlap:
            raise ValueError(f"Hai gia una prenotazione sovrapposta: {overlap['title']}.")

        existing = conn.execute(
            """
            SELECT * FROM reservations
            WHERE user_id = ? AND tour_id = ? AND tour_date = ?
            """,
            (current_user.id, id, tour_date.isoformat()),
        ).fetchone()
        if existing and existing["status"] == "booked":
            raise ValueError("Hai gia prenotato questo tour in questa data.")
        if existing and existing["status"] == "cancelled":
            conn.execute(
                """
                UPDATE reservations
                SET num_people = ?, extra_names = ?, status = 'booked', cancelled_at = NULL
                WHERE id = ?
                """,
                (num_people, ", ".join(names), existing["id"]),
            )
        else:
            conn.execute(
                """
                INSERT INTO reservations (user_id, tour_id, tour_date, num_people, extra_names)
                VALUES (?, ?, ?, ?, ?)
                """,
                (current_user.id, id, tour_date.isoformat(), num_people, ", ".join(names)),
            )
        conn.commit()
        flash("Prenotazione confermata.", "success")
    except ValueError as exc:
        flash(str(exc), "danger")
    except IntegrityError:
        flash("Prenotazione gia presente per questa data.", "danger")
    finally:
        conn.close()
    return redirect(url_for("tour_detail", id=id))


@app.route("/tour/<int:id>/comment", methods=["POST"])
def add_comment(id):
    if not current_user.is_authenticated:
        flash("Accedi per commentare.", "warning")
        return redirect(url_for("login", next=url_for("tour_detail", id=id)))

    conn = get_db_connection()
    if not get_tour_row(conn, id):
        conn.close()
        abort(404)
    text = (request.form.get("text") or "").strip()
    if len(text) < 2:
        flash("Il commento e troppo breve.", "danger")
    elif len(text) > 600:
        flash("Il commento non puo superare 600 caratteri.", "danger")
    else:
        conn.execute(
            """
            INSERT INTO comments (tour_id, user_id, publication_date, text)
            VALUES (?, ?, ?, ?)
            """,
            (id, current_user.id, dt.date.today().isoformat(), text),
        )
        conn.commit()
        flash("Commento pubblicato.", "success")
    conn.close()
    return redirect(url_for("tour_detail", id=id))


@app.route("/profile")
@login_required
def profile():
    if current_user.role == "guide":
        return redirect(url_for("guide_profile"))
    return redirect(url_for("participant_profile"))


@app.route("/participant/profile")
@login_required
def participant_profile():
    denied = require_role("participant")
    if denied:
        return denied

    conn = get_db_connection()
    rows = conn.execute(
        """
        SELECT reservations.*, tours.title, tours.meeting_point, tours.duration_mins,
               tours.language, users.first_name AS guide_first_name,
               users.last_name AS guide_last_name
        FROM reservations
        JOIN tours ON tours.id = reservations.tour_id
        JOIN users ON users.id = tours.guide_id
        WHERE reservations.user_id = ?
        ORDER BY reservations.tour_date DESC, reservations.id DESC
        """,
        (current_user.id,),
    ).fetchall()

    reservations = []
    now = dt.datetime.now()
    for row in rows:
        item = dict(row)
        tour_date = parse_iso_date(row["tour_date"])
        schedule = get_schedule_for_date(conn, row["tour_id"], tour_date)
        item["start_time"] = schedule["start_time"] if schedule else "-"
        item["can_cancel"] = False
        if row["status"] == "booked" and schedule:
            start_dt = tour_datetime(tour_date, schedule["start_time"])
            item["can_cancel"] = start_dt - now >= dt.timedelta(hours=24)
        reservations.append(item)
    conn.close()
    return render_template("participant_profile.html", reservations=reservations)


@app.route("/reservation/<int:reservation_id>/cancel", methods=["POST"])
@login_required
def cancel_reservation(reservation_id):
    denied = require_role("participant")
    if denied:
        return denied

    conn = get_db_connection()
    reservation = conn.execute(
        "SELECT * FROM reservations WHERE id = ? AND user_id = ?",
        (reservation_id, current_user.id),
    ).fetchone()
    if not reservation:
        conn.close()
        abort(404)
    if reservation["status"] != "booked":
        flash("Questa prenotazione e gia stata annullata.", "warning")
        conn.close()
        return redirect(url_for("participant_profile"))

    tour_date = parse_iso_date(reservation["tour_date"])
    schedule = get_schedule_for_date(conn, reservation["tour_id"], tour_date)
    if not schedule or tour_datetime(tour_date, schedule["start_time"]) - dt.datetime.now() < dt.timedelta(hours=24):
        flash("Puoi annullare solo almeno 24 ore prima dell'inizio del tour.", "danger")
        conn.close()
        return redirect(url_for("participant_profile"))

    conn.execute(
        """
        UPDATE reservations
        SET status = 'cancelled', cancelled_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (reservation_id,),
    )
    conn.commit()
    conn.close()
    flash("Prenotazione annullata.", "success")
    return redirect(url_for("participant_profile"))


@app.route("/guide/profile")
@login_required
def guide_profile():
    denied = require_role("guide")
    if denied:
        return denied

    conn = get_db_connection()
    rows = conn.execute(
        """
        SELECT tours.*, users.first_name AS guide_first_name,
               users.last_name AS guide_last_name
        FROM tours
        JOIN users ON users.id = tours.guide_id
        WHERE guide_id = ?
        ORDER BY tours.created_at DESC, tours.id DESC
        """,
        (current_user.id,),
    ).fetchall()
    tours = []
    now = dt.datetime.now()
    for row in rows:
        tour = enrich_tour(conn, row)
        groups = conn.execute(
            """
            SELECT tour_date, COUNT(*) AS reservation_count,
                   COALESCE(SUM(num_people), 0) AS people_count
            FROM reservations
            WHERE tour_id = ? AND status = 'booked'
            GROUP BY tour_date
            ORDER BY tour_date
            """,
            (tour["id"],),
        ).fetchall()
        tour["reservation_dates"] = []
        for group in groups:
            tour_date = parse_iso_date(group["tour_date"])
            schedule = get_schedule_for_date(conn, tour["id"], tour_date)
            start_time = schedule["start_time"] if schedule else "-"
            start_dt = tour_datetime(tour_date, start_time) if schedule else None
            report = conn.execute(
                "SELECT * FROM tour_reports WHERE tour_id = ? AND tour_date = ?",
                (tour["id"], group["tour_date"]),
            ).fetchone()
            reservations = conn.execute(
                """
                SELECT reservations.*, users.first_name, users.last_name, users.email
                FROM reservations
                JOIN users ON users.id = reservations.user_id
                WHERE reservations.tour_id = ?
                  AND reservations.tour_date = ?
                  AND reservations.status = 'booked'
                ORDER BY reservations.id
                """,
                (tour["id"], group["tour_date"]),
            ).fetchall()
            tour["reservation_dates"].append(
                {
                    "date": group["tour_date"],
                    "start_time": start_time,
                    "reservation_count": group["reservation_count"],
                    "people_count": group["people_count"],
                    "reservations": reservations,
                    "report": report,
                    "can_report": bool(start_dt and start_dt < now),
                }
            )
        tours.append(tour)
    conn.close()
    return render_template("guide_profile.html", tours=tours)


@app.route("/guide/report/<int:tour_id>/<tour_date>", methods=["POST"])
@login_required
def submit_report(tour_id, tour_date):
    denied = require_role("guide")
    if denied:
        return denied

    conn = get_db_connection()
    tour = get_tour_row(conn, tour_id)
    if not tour:
        conn.close()
        abort(404)
    if tour["guide_id"] != int(current_user.id):
        conn.close()
        abort(403)

    try:
        parsed_date = parse_iso_date(tour_date)
        schedule = get_schedule_for_date(conn, tour_id, parsed_date)
        if not schedule:
            raise ValueError("Questa data non appartiene allo schedule del tour.")
        if tour_datetime(parsed_date, schedule["start_time"]) >= dt.datetime.now():
            raise ValueError("Il report puo essere inviato solo dopo lo svolgimento del tour.")

        expected = active_reserved_places(conn, tour_id, parsed_date)
        if expected <= 0:
            raise ValueError("Non ci sono prenotazioni per questa data.")
        actual = parse_positive_int(
            request.form.get("actual_participants"),
            "Partecipanti effettivi",
            0,
            expected,
        )
        file = request.files.get("evidence_photo")
        if not validate_file(file):
            raise ValueError("Carica una foto prova valida.")
        photo_path = save_uploaded_file(file, f"report-{tour_id}-{tour_date}")

        conn.execute(
            """
            INSERT INTO tour_reports (tour_id, tour_date, actual_participants, evidence_photo)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(tour_id, tour_date) DO UPDATE SET
                actual_participants = excluded.actual_participants,
                evidence_photo = excluded.evidence_photo,
                created_at = CURRENT_TIMESTAMP
            """,
            (tour_id, tour_date, actual, photo_path),
        )
        conn.commit()
        flash("Report salvato.", "success")
    except ValueError as exc:
        flash(str(exc), "danger")
    finally:
        conn.close()
    return redirect(url_for("guide_profile"))


@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
