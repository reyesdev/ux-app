# routes/auth_routes.py
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_bcrypt import Bcrypt
from flask_login import login_user, login_required, logout_user, current_user, LoginManager
from models import User, execute_query
from .extensions import login_manager

auth_bp = Blueprint('auth', __name__)
bcrypt = Bcrypt()

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = execute_query('SELECT * FROM users WHERE username=%s', (username,), fetchone=True)

        if user and bcrypt.check_password_hash(user['password'], password):
            user_obj = User(user['id'], user['username'])  # Create a User object
            login_user(user_obj)  # Log in the user
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login unsuccessful. Please check your username and password.', 'danger')

    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        existing_user = execute_query('SELECT * FROM users WHERE username=%s', (username,), fetchone=True)
        if existing_user:
            flash('Username already taken. Please choose another.', 'danger')
        else:
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            execute_query('INSERT INTO users (username, password) VALUES (%s, %s)', (username, hashed_password), commit=True)

            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth_bp.route('/logout')
@login_required  # Ensures that only logged-in users can log out
def logout():
    logout_user()  # Log out the current user
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@auth_bp.route('/profile')
@login_required  # Ensures that only logged-in users can access the profile page
def profile():
    return render_template('profile.html', user=current_user)

# Initialize the login manager (outside the function)
login_manager.login_view = 'auth.login'

# Function to initialize auth routes
def init_auth_routes(app):
    app.register_blueprint(auth_bp)
