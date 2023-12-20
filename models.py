import mysql.connector
import config
from flask_login import UserMixin
from flask_bcrypt import Bcrypt  # Import Bcrypt for password hashing

db_config = config.dbconfig
bcrypt = Bcrypt()

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

class User(UserMixin):
    def __init__(self, user_id, username, password=None):
        self.id = user_id
        self.username = username
        self.password = password

    @staticmethod
    def get(user_id):
        query = 'SELECT * FROM users WHERE id = %s'
        result = execute_query(query, (user_id,), fetchone=True)

        if result:
            user = User(user_id=result['id'], username=result['username'])
            return user
        else:
            return None

    @staticmethod
    def get_by_username(username):
        query = 'SELECT * FROM users WHERE username = %s'
        result = execute_query(query, (username,), fetchone=True)

        if result:
            user = User(user_id=result['id'], username=result['username'], password=result['password'])
            return user
        else:
            return None

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def save(self):
        if not self.id:
            # Insert a new user
            query = 'INSERT INTO users (username, password) VALUES (%s, %s)'
            execute_query(query, (self.username, self.password), commit=True)
        else:
            # Update an existing user
            query = 'UPDATE users SET username=%s, password=%s WHERE id=%s'
            execute_query(query, (self.username, self.password, self.id), commit=True)
