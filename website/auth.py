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

        # Check if the password is empty
        if not password:
            flash('Password is required.', category='error')
            return render_template('login.html')
        
        try:
            cursor = g.db.cursor(dictionary=True)
            query = "SELECT * FROM User WHERE email = %s"
            cursor.execute(query, (email,))
            user_data = cursor.fetchone()
        except mysql.connector.Error as e:
            print(f"MySQL error occurred: {e}")
        finally:
            if cursor:
                cursor.close()
        
        if user_data:
            user = User.from_dict(user_data)  # Convert dictionary to User object
            if check_password_hash(user.password, password):  # Use check_password_hash
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
    flash('You have been logged out successfully.', category='success')
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    # Initialize form_data to ensure it exists even if an error occurs
    form_data = {
        'email': '',
        'full_name': ''
    }
    if request.method == 'POST': 
        email = request.form.get('email')
        full_name = request.form.get('fullName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        # Update form_data with current form inputs
        form_data = {
            'email': email,
            'full_name': full_name
        }

        try:
            cursor = g.db.cursor(dictionary=True)
            cursor.execute("SELECT * FROM User WHERE email = %s", (email,))
            user_data = cursor.fetchone()

            if user_data:
                flash('This email is already registered.', category='error')
            elif len(email) < 4:
                flash('Email must be longer than 3 characters.', category='error')
            elif len(full_name) < 2:
                flash('Your name must be longer than 1 character.', category='error')
            elif password1 != password2:
                flash('Passwords do not match.', category='error')
            elif len(password1) < 6:
                flash('Password must be at least 6 characters long.', category='error')
            else:
                #  Ensure the password is hashed properly
                hashed_password = generate_password_hash(password1, method='scrypt')
                insert_query = """
                    INSERT INTO User (email, password, full_name) 
                    VALUES (%s, %s, %s)
                """
                cursor.execute(insert_query, (email, hashed_password, full_name))
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
            if cursor:
                cursor.close()
    
    return render_template('signup.html', form_data=form_data)
