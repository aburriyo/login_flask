from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'  # Cambia esto a una clave segura

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        action = request.form['action']
        username = request.form['username']
        password = request.form['password']
        
        if action == 'Register':
            confirm_password = request.form['confirm_password']
            if password != confirm_password:
                flash('Las contraseñas no coinciden')
                return redirect(url_for('index'))

            conn = get_db_connection()
            try:
                conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
                conn.commit()
                flash('Usuario registrado exitosamente')
            except sqlite3.IntegrityError:
                flash('El nombre de usuario ya existe')
            finally:
                conn.close()
        
        elif action == 'Login':
            conn = get_db_connection()
            user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
            conn.close()
            if user:
                session['username'] = username
                flash('Inicio de sesión exitoso')
                return redirect(url_for('dashboard'))
            else:
                flash('Credenciales inválidas')

    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return f'Bienvenido, {session["username"]} <a href="/logout">Cerrar sesión</a>'
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Sesión cerrada')
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
