from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3, random
from datetime import date

app = Flask(__name__)
app.secret_key = ""

# ---------- DATABASE SETUP ----------
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS diary (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    entry TEXT,
                    date TEXT)''')
    conn.commit()
    conn.close()

init_db()



# ---------- ROUTES ----------
@app.route('/')
def index():
    return redirect(url_for('login'))



@app.route('/login', methods=['GET', 'POST'])

def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            session['username'] = username
            # ✅ CHANGE: redirect to mental health form instead of dashboard
            return redirect(url_for('mental_health'))
        else:
            return render_template('login.html', error="Invalid credentials")

    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        try:
            c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return render_template('signup.html', error="Username already exists")

    return render_template('signup.html')

# ---------- HOME ----------
@app.route('/home')
def home():
    if 'username' in session:
        return render_template('home.html', username=session['username'])
    return redirect(url_for('login'))

# ---------- MENTAL HEALTH FORM ----------
@app.route('/mental-health', methods=['GET', 'POST'])
def mental_health():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        responses = {
            'q1': request.form.get('q1'),
            'q2': request.form.get('q2'),
            'q3': request.form.get('q3'),
            'q4': request.form.get('q4'),
            'q5': request.form.get('q5')
        }
        print("User responses:", responses)
        return redirect(url_for('dashboard'))

    return render_template('mental_health.html', username=session['username'])

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']

    if request.method == 'POST':
        entry = request.form['diary_entry']
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('INSERT INTO diary (username, entry, date) VALUES (?, ?, ?)',
                  (username, entry, str(date.today())))
        conn.commit()
        conn.close()

    thoughts = random.sample([
        "You are enough just as you are 🌼",
        "Every day is a new beginning ☀️",
        "You are stronger than you think 💪",
        "Peace begins when you let go of negativity 🌿",
        "It’s okay to rest; you’re still growing 🌸",
        "Your presence makes the world better 💖"
    ], 3)
    return render_template('dashboard.html', username=username, thoughts=thoughts)

@app.route('/therapists')
def therapists():
    if 'username' not in session:
        return redirect(url_for('login'))
    therapist_list = [
        {"name": "Dr. Anjali Sharma", "contact": "+91 9876543210"},
        {"name": "Dr. Rohan Mehta", "contact": "+91 8765432109"},
        {"name": "Dr. Priya Nair", "contact": "+91 9123456780"}
    ]
    return render_template('therapists.html', therapists=therapist_list)

# ---------- LOGOUT ----------
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# ---------- MAIN ----------
if __name__ == '__main__':
    app.run(debug=True)
