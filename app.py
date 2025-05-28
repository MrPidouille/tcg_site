from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'ton_secret_key_ici'  # Change ça

DATABASE = 'tcg.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Création base (à lancer une fois)
def init_db():
    with app.app_context():
        db = get_db()
        with open('schema.sql', 'r') as f:
            db.executescript(f.read())
        db.commit()

# Décorateur login requis
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Connecte-toi d'abord !")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Décorateur admin requis
def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Connecte-toi d'abord !")
            return redirect(url_for('login'))
        if not session.get('is_admin'):
            flash("Accès refusé.")
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('collection'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        try:
            db.execute('INSERT INTO users (username,password) VALUES (?,?)',
                       (username, generate_password_hash(password)))
            db.commit()
            flash("Compte créé, connecte-toi !")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Nom d'utilisateur déjà pris.")
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['is_admin'] = user['is_admin']
            flash("Connecté !")
            return redirect(url_for('collection'))
        flash("Mauvais identifiants.")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Déconnecté.")
    return redirect(url_for('login'))

@app.route('/pack', methods=['GET', 'POST'])
@login_required
def pack():
    db = get_db()
    cards = db.execute('SELECT * FROM cards').fetchall()
    if request.method == 'POST':
        card_id = request.form.get('card')
        quantity = int(request.form.get('quantity', 1))
        user_id = session['user_id']

        # Vérifier si l'utilisateur a déjà la carte
        existing = db.execute('SELECT * FROM user_cards WHERE user_id = ? AND card_id = ?', (user_id, card_id)).fetchone()
        if existing:
            db.execute('UPDATE user_cards SET quantity = quantity + ? WHERE id = ?', (quantity, existing['id']))
        else:
            db.execute('INSERT INTO user_cards (user_id, card_id, quantity) VALUES (?, ?, ?)', (user_id, card_id, quantity))
        db.commit()
        flash(f"{quantity} carte(s) ajoutée(s) à ta collection.")
        return redirect(url_for('collection'))
    return render_template('pack.html', cards=cards)

@app.route('/collection')
@login_required
def collection():
    db = get_db()
    user_id = session['user_id']
    # Récupérer les cartes de l’utilisateur
    user_cards = db.execute('''
        SELECT c.name, c.edition, c.rarity, c.price, uc.quantity 
        FROM user_cards uc
        JOIN cards c ON uc.card_id = c.id
        WHERE uc.user_id = ?
    ''', (user_id,)).fetchall()
    return render_template('collection.html', user_cards=user_cards)

@app.route('/admin', methods=['GET', 'POST'])
@admin_required
def admin():
    db = get_db()
    if request.method == 'POST':
        name = request.form['name']
        edition = request.form['edition']
        rarity = request.form['rarity']
        price = int(request.form['price'])
        db.execute('INSERT INTO cards (name, edition, rarity, price) VALUES (?, ?, ?, ?)', (name, edition, rarity, price))
        db.commit()
        flash("Carte ajoutée.")
        return redirect(url_for('admin'))
    cards = db.execute('SELECT * FROM cards').fetchall()
    return render_template('admin.html', cards=cards)

if __name__ == '__main__':
    app.run(debug=True)
