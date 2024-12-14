from os import path
from flask import Flask, g
from flask_login import LoginManager
import mysql.connector

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'supersecretkey'

    # Blueprints for modularity
    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User  # Import the User class
    @login_manager.user_loader
    def load_user(user_id):
        if user_id == '1':  # Do not restore the admin user
            return None
        try:
            cursor = g.db.cursor(dictionary=True)
            query = "SELECT * FROM User WHERE id = %s"
            cursor.execute(query, (user_id,))
            user_data = cursor.fetchone()  # This gets the user data as a dictionary
        except mysql.connector.Error as e:
            print(f"MySQL error occurred: {e}")
            user_data = None
        finally:
            cursor.close()

        if user_data:
            return User.from_dict(user_data)  # Convert the dictionary into a User object
        return None  # Return None if user not found


    @app.before_request
    def connect_to_database():
        """
        Establishes a connection to the MySQL database before each request.
        """
        if 'db' not in g:
            g.db = mysql.connector.connect(
                host='localhost',
                user='root',
                password='1234',
                database='3kan'
            )

    @app.teardown_request
    def close_database_connection(exception=None):
        """
        Closes the MySQL connection after each request.
        """
        db = g.pop('db', None)
        if db is not None:
            db.close()

    return app
