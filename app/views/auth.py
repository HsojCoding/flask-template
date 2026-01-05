from flask import Blueprint, request, redirect, url_for, render_template, flash, current_user
from flask_login import login_user, login_required
from app.db.models import User
from werkzeug.security import check_password_hash
from app.auth import admin_required
from datetime import datetime, timezone
from app.auth import bcrypt
from app.db import db

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
            flash('Invalid username or password', 'error')
            return redirect(url_for('auth_bp.login'))
    return render_template('auth/login.html')

@auth_bp.route('/create_user', methods=['GET', 'POST'])
@login_required # ensure there is a current user logged in
@admin_required # ensure the current user is an admin
def create_user():
    if request.method == 'POST':

        # Check if the username is already taken
        if User.query.filter_by(username=request.form['username']).first():
            flash('Username already taken', 'error')
            return redirect(url_for('auth_bp.create_user'))
        # Check if the email is already taken
        if User.query.filter_by(email=request.form['email']).first():
            flash('Email already taken', 'error')
            return redirect(url_for('auth_bp.create_user'))

        # Create the user
        user = User(
            # Id will auto-increment in db
            username=request.form['username'],
            email=request.form['email'],
            password=bcrypt.generate_password_hash(request.form['password']).decode('utf-8'),
            is_admin= True if request.form['is_admin'] else False,
            active= True, # User should be active on creation
            updated_by_id=current_user.id,
            updated_datetime=datetime.now(timezone.utc)
        )

        try:
            db.session.add(user)
            db.session.commit()
            flash('User created successfully', 'success')
            return redirect(url_for('auth_bp.create_user'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error creating user: {e}', 'error')
            return redirect(url_for('auth_bp.create_user'))

    # Render the create user form
    return render_template('auth/create_user.html')