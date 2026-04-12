from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from DataBase.database import create_user, get_user_by_email, get_user_by_username

auth = Blueprint('auth', __name__)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username      = request.form.get('username', '').strip()
        email_address = request.form.get('email_address', '').strip().lower()
        password      = request.form.get('password', '')
        confirm       = request.form.get('confirm_password', '')

        # ── Validation ──────────────────────────────────────────────
        if not username or not email_address or not password:
            flash('All fields are required.', 'error')
            return render_template('register.html')

        if len(username) < 3:
            flash('Username must be at least 3 characters.', 'error')
            return render_template('register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'error')
            return render_template('register.html')

        if password != confirm:
            flash('Passwords do not match.', 'error')
            return render_template('register.html')

        if get_user_by_username(username):
            flash('Username is already taken.', 'error')
            return render_template('register.html')

        if get_user_by_email(email_address):
            flash('An account with that email already exists.', 'error')
            return render_template('register.html')

        # ── Create user ──────────────────────────────────────────────
        password_hash = generate_password_hash(password)
        user_id = create_user(username, password_hash, email_address)

        if user_id is None:
            flash('Could not create account. Please try again.', 'error')
            return render_template('register.html')

        session['user_id']  = user_id
        session['username'] = username
        return redirect(url_for('home'))

    return render_template('register.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email_address = request.form.get('email_address', '').strip().lower()
        password      = request.form.get('password', '')

        if not email_address or not password:
            flash('Please enter your email and password.', 'error')
            return render_template('login.html')

        user = get_user_by_email(email_address)

        if not user or not check_password_hash(user['password_hash'], password):
            flash('Invalid email or password.', 'error')
            return render_template('login.html')

        session['user_id']  = user['user_id']
        session['username'] = user['username']
        return redirect(url_for('home'))

    return render_template('login.html')


@auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))