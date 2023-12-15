import logging
from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_bcrypt import Bcrypt
import mysql.connector

app = Flask(__name__)
app.secret_key = 'Amm0$3cr3+k3y'  # Change this to a random secret key
bcrypt = Bcrypt()


# Configure the logging to a file
handler = logging.FileHandler('error.log')
handler.setLevel(logging.ERROR)
app.logger.addHandler(handler)

# Connect to MySQL
db_config = {
    'host': 'localhost',
    'user': 'ammo',
    'password': 'Tendre143?',
    'database': 'user',
    'port': '3306',
}

# Using a context manager for database connection and cursor
def execute_query(query, data=None, fetchone=False, fetchall=False):
    with mysql.connector.connect(**db_config) as connection:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute(query, data)

            # Only commit for write operations
            if query.strip().split()[0].upper() in ["INSERT", "UPDATE", "DELETE"]:
                connection.commit()

            if fetchone:
                return cursor.fetchone()
            elif fetchall:
                return cursor.fetchall()
            return None

# Create a 'users' table if it doesn't exist
execute_query('''
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(255) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL
    )
''')

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = execute_query('SELECT * FROM users WHERE username=%s', (username,), fetchone=True)

        if user and bcrypt.check_password_hash(user['password'], password):
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login unsuccessful. Please check your username and password.', 'danger')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Validate if the username is already taken
        existing_user = execute_query('SELECT * FROM users WHERE username=%s', (username,), fetchone=True)
        if existing_user:
            flash('Username already taken. Please choose another.', 'danger')
        else:
            # Hash the password before storing it
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

            # Insert the new user into the 'users' table
            execute_query('INSERT INTO users (username, password) VALUES (%s, %s)', (username, hashed_password))

            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
