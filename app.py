import logging
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import User
import mysql.connector
import config

app = Flask(__name__)
app.secret_key = config.secretkey  # Change this to a random secret key
login_manager = LoginManager(app)

# Load user from the database
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# Configure the login view
login_manager.login_view = 'login'

# Configure the logging to a file
handler = logging.FileHandler('error.log')
handler.setLevel(logging.ERROR)
app.logger.addHandler(handler)

# Connect to MySQL
db_config = config.dbconfig

# Using a context manager for database connection and cursor
def execute_query(query, data=None, fetchone=False, fetchall=False, commit=False):
    with mysql.connector.connect(**db_config) as connection:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute(query, data)

            if commit:
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
''', commit=True)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.get_by_username(username)

        if user and user.check_password(password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('profile'))
        else:
            flash('Login unsuccessful. Please check your username and password.', 'danger')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        existing_user = User.get_by_username(username)
        if existing_user:
            flash('Username already taken. Please choose another.', 'danger')
        else:
            new_user = User(username=username)
            new_user.set_password(password)
            new_user.save()

            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@app.route('/')
def home():
    return 'Home Page'

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
