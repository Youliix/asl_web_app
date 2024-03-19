from flask import Blueprint, render_template, session, request, jsonify, make_response
from . import db

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if 'firstname' in session:
        return render_template('index.html', main_template="./content/homepage.html", firstname=session['firstname'])
    else:
        return render_template('index.html', main_template="./content/homepage.html")


@main.route('/profile', methods=['GET', 'PUT'])
def profile():
    if request.method == 'PUT':
        data = request.get_json()

        if data['rgpd_right'] is None:
            data['rgpd_right']  = False
        else:
            data['rgpd_right']  = True

        data['id'] = session['user_id']

        db.update_user(data)
        user = db.get_user(session['user_id'])
        session['firstname'] = user[0]
        session['rgpd_right'] = user[2]
        return make_response(jsonify({'firstname': user[0]}), 200)
    
    if 'firstname' not in session:
        return render_template('index.html', main_template='./content/login.html', error='You are not logged in. Please log in to view this page.')
    
    user = db.get_user(session['user_id'])
    return render_template('index.html', main_template='./content/profile.html', firstname=session['firstname'], user=user)