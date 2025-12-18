from flask import Blueprint, request, redirect, url_for, render_template
from flask_login import login_user
from app.db.models import User
from werkzeug.security import check_password_hash

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('main_bp.index'))
        else:
            return redirect(url_for('auth_bp.login', error='Invalid username or password'))
    return render_template('auth/login.html')