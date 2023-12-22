# app.py
import logging
from flask import Flask
from models import execute_query
import mysql.connector
import config
from routes.extensions import login_manager
from routes.auth_routes import init_auth_routes

app = Flask(__name__)
app.secret_key = config.secretkey

# Initialize the login manager
login_manager.login_view = 'auth.login'  # Set the login view
login_manager.init_app(app)

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

            # Commit if specified
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

# Initialize the auth routes with the app object
init_auth_routes(app)

@app.route('/')
def home():
    return 'Home Page'

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
