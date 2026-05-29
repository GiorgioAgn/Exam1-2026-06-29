import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import datetime
from db import get_db_connection

app = Flask(__name__)
app.secret_key = 'super_chiave_segreta_esame'

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True) # Crea la cartella se non esiste
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, email, role, first_name, last_name):
        self.id = id
        self.email = email
        self.role = role
        self.first_name = first_name
        self.last_name = last_name

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    user_row = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    if user_row:
        return User(user_row['id'], user_row['email'], user_row['role'], user_row['first_name'], user_row['last_name'])
    return None

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- ROTTE ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/hiking')
def hiking():
    conn = get_db_connection()
    query = '''
        SELECT tours.*, users.first_name, users.last_name 
        FROM tours JOIN users ON tours.guide_id = users.id
    '''
    tours = conn.execute(query).fetchall()
    conn.close()
    return render_template('hiking.html', tours=tours)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_db_connection()
        user_row = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()
        
        if user_row and check_password_hash(user_row['password'], password):
            user_obj = User(user_row['id'], user_row['email'], user_row['role'], user_row['first_name'], user_row['last_name'])
            login_user(user_obj)
            return redirect(url_for('index'))
        else:
            flash('Credenziali errate.', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        hashed_password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')
        conn = get_db_connection()
        try:
            conn.execute('''
                INSERT INTO users (first_name, last_name, email, password, role, languages) 
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (request.form['first_name'], request.form['last_name'], request.form['email'], hashed_password, request.form['role'], request.form.get('languages', '')))
            conn.commit()
            flash('Registrato! Ora accedi.', 'success')
            return redirect(url_for('login'))
        except:
            flash('Email già in uso.', 'danger')
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/create-tour', methods=['GET', 'POST'])
@login_required
def create_tour():
    if current_user.role != 'guide': return redirect(url_for('index'))
    if request.method == 'POST':
        file = request.files.get('photo1')
        filename_to_save = None
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            filename_to_save = f'/static/uploads/{filename}'
            
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO tours (guide_id, title, meeting_point, duration_mins, language, max_partecipants, description, stops, photo1)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (current_user.id, request.form['title'], request.form['meeting_point'], request.form['duration_mins'], request.form['language'], request.form['max_partecipants'], request.form['description'], request.form['stops'], filename_to_save))
        conn.commit()
        conn.close()
        flash('Tour creato!', 'success')
        return redirect(url_for('hiking'))
    return render_template('create_tour.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/tour/<int:id>', methods=['GET', 'POST'])
def tour_detail(id):
    conn = get_db_connection()
    tour = conn.execute('SELECT * FROM tours WHERE id = ?', (id,)).fetchone()
    guide = conn.execute('SELECT first_name, last_name FROM users WHERE id = ?', (tour['guide_id'],)).fetchone()

    if request.method == 'POST':
        action = request.form.get('action_type')
        if action == 'booking':
            conn.execute('INSERT INTO reservations (user_id, tour_id, tour_date, num_people, extra_names) VALUES (?, ?, ?, ?, ?)', 
                         (current_user.id, id, request.form['tour_date'], request.form['num_people'], request.form['extra_names']))
            conn.commit()
            flash('Prenotato!', 'success')
        elif action == 'comment':
            anonymous = request.form.get('anonymous')
            user_id_to_save = None if anonymous else current_user.id
            c_file = request.files.get('comment_image')
            c_path = None
            if c_file and allowed_file(c_file.filename):
                fname = secure_filename(c_file.filename)
                c_file.save(os.path.join(app.config['UPLOAD_FOLDER'], fname))
                c_path = f'/static/uploads/{fname}'
            oggi = datetime.date.today().strftime("%Y-%m-%d")
            conn.execute('INSERT INTO comments (publication_date, text, post_id, user_id, rating, comment_image) VALUES (?, ?, ?, ?, ?, ?)', 
                         (oggi, request.form['text'], id, user_id_to_save, request.form['rating'], c_path))
            conn.commit()

    comments = conn.execute('SELECT comments.*, users.first_name FROM comments LEFT JOIN users ON comments.user_id = users.id WHERE comments.post_id = ? ORDER BY comments.id DESC', (id,)).fetchall()
    conn.close()
    return render_template('tour_detail.html', tour=tour, guide=guide, comments=comments)

if __name__ == '__main__':
    app.run(debug=True)