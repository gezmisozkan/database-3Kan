from os import path
from flask import Flask, g
from flask_login import LoginManager
import mysql.connector

DB_NAME = "../database.db"  # Unused, but kept for reference

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'Hakan1234'

    # Blueprints for modularity
    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        try:
            cursor = g.db.cursor(dictionary=True)
            query = "SELECT * FROM User WHERE id = %s"
            cursor.execute(query, (user_id,))
            user = cursor.fetchone()
        except mysql.connector.Error as e:
            print(f"MySQL error occurred: {e}")
            user = None
        finally:
            cursor.close()

        return user

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
