from flask import Blueprint, flash, render_template, request, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user
import mysql.connector
from flask import g
from .models import User  # Import the User class

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        try:
            cursor = g.db.cursor(dictionary=True)
            query = "SELECT * FROM User WHERE email = %s"
            cursor.execute(query, (email,))
            user_data = cursor.fetchone()
        except mysql.connector.Error as e:
            print(f"MySQL error occurred: {e}")
        finally:
            cursor.close()
        
        if user_data:
            user = User.from_dict(user_data)  # Convert dictionary to User object
            if user.password == password:  # Assuming plain text password for simplicity
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)  # Pass the User object to login_user()
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')
    
    return render_template('login.html')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST': 
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        try:
            cursor = g.db.cursor(dictionary=True)
            cursor.execute("SELECT * FROM User WHERE email = %s", (email,))
            user_data = cursor.fetchone()

            if user_data:
                flash('Email already exists.', category='error')
            elif len(email) < 4:
                flash('Email must be greater than 3 characters.', category='error')
            elif len(first_name) < 2:
                flash('First name must be greater than 1 character.', category='error')
            elif password1 != password2:
                flash('Passwords do not match.', category='error')
            elif len(password1) < 7:
                flash('Password must be greater than 6 characters.', category='error')
            else:
                hashed_password = generate_password_hash(password1, method='scrypt')
                insert_query = """
                    INSERT INTO User (email, password, first_name) 
                    VALUES (%s, %s, %s)
                """
                cursor.execute(insert_query, (email, hashed_password, first_name))
                g.db.commit()

                cursor.execute("SELECT * FROM User WHERE email = %s", (email,))
                new_user_data = cursor.fetchone()
                new_user = User.from_dict(new_user_data)  # Convert to User object
                login_user(new_user, remember=True)
                flash('Account created successfully!', category='success')
                return redirect(url_for('views.home'))
        except mysql.connector.Error as e:
            print(f"MySQL error occurred: {e}")
        finally:
            cursor.close()
    
    return render_template('signup.html')
