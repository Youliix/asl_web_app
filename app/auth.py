from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

from . import db
from flask import Blueprint

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', None)
        password = request.form.get('password', None)
        conn = db.get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()

        if user and check_password_hash(user[4], password):
            session['firstname'] = user[1]
            session['rgpd_right'] = user[5]
            session['user_id'] = user[0]
            conn.close()
            return redirect(url_for('main.index'))
        else:
            conn.close()
            flash('L\'utilisateur n\'existe pas ou le mot de passe est incorrect')
            return render_template('index.html', main_template='./content/login.html')

    return render_template('index.html', main_template='./content/login.html')


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email',  None)
        firstname = request.form.get('firstname', None)
        lastname = request.form.get('lastname', None)
        password = request.form.get('password', None)
        rgpd_right = request.form.get('rgpd_right', None)
        
        if rgpd_right is None:
            rgpd_right = False
        else:
            rgpd_right = True
        conn = db.get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        if user:
            cur.close()
            conn.close()
            flash('L\'utilisateur existe déjà')
            return redirect(url_for('auth.signup'))

        hashed_password = generate_password_hash(password)
        cur.execute("INSERT INTO users (email, firstname, lastname, password, rgpd_right) VALUES (%s, %s, %s, %s, %s)", (email, firstname, lastname, hashed_password, rgpd_right,))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('auth.login'))
    
    return render_template('index.html', main_template='./content/signup.html')


@auth.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('firstname', None)
    session.pop('rgpd_right', None)
    return redirect(url_for('main.index'))
