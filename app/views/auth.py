from flask import Blueprint, request, redirect, url_for, render_template, flash, current_app
from flask_login import login_user, login_required, current_user, logout_user
from datetime import datetime, timezone
import click
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError

from app.auth import admin_required
from app.auth import bcrypt
from app.db import db
from app.db.models import User


auth_bp = Blueprint('auth', __name__)

@auth_bp.cli.command('create-superuser')
@click.argument('username')
@click.argument('email')
@click.argument('password')
def create_superuser(username, email, password):
    if not username or not email or not password:
        click.echo('Username, email, and password are required')
        return
    if User.query.filter_by(username=username).first():
        click.echo('Username already taken')
        return
    if User.query.filter_by(email=email).first():
        click.echo('Email already taken')
        return
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    user = User(username=username, email=email, password=hashed_password, is_admin=True, active=True)
    db.session.add(user)
    
    try:
        db.session.commit()
        click.echo(f'Superuser {username} created successfully')

    except IntegrityError as e:
        db.session.rollback()
        current_app.logger.error(f'Integrity error creating superuser: {e}')
        click.echo(f'Integrity error creating superuser: {e}')
        return

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error creating superuser: {e}')
        click.echo(f'Error creating superuser: {e}')
        return

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('main.index'))
        else:
            current_app.logger.error(f'Invalid username or password for user {username}')
            flash('Invalid username or password', "error")
            return redirect(url_for('auth.login'))
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/create_user', methods=['GET', 'POST'])
@login_required # ensure there is a current user logged in
@admin_required # ensure the current user is an admin
def create_user():
    if request.method == 'POST':

        # Check if the username is already taken
        if User.query.filter_by(username=request.form['username']).first():
            current_app.logger.error(f'Username already taken for user {request.form['username']}')
            flash('Username already taken', "error")
            return redirect(url_for('auth.create_user'))
        # Check if the email is already taken
        if User.query.filter_by(email=request.form['email']).first():
            current_app.logger.error(f'Email already taken for user {request.form['email']}')
            flash('Email already taken', "error")
            return redirect(url_for('auth.create_user'))

        # Create the user
        user = User(
            # Id will auto-increment in db
            username=request.form['username'],
            email=request.form['email'],
            password=bcrypt.generate_password_hash(request.form['password']).decode('utf-8'),
            is_admin=bool(request.form.get('is_admin')),
            active= True, # User should be active on creation
            updated_by_id=current_user.id,
            updated_datetime=datetime.now(timezone.utc)
        )

        try:
            db.session.add(user)
            db.session.commit()
            flash('User created successfully', 'success')
            return redirect(url_for('auth.create_user'))

        except IntegrityError as e:
            db.session.rollback()
            current_app.logger.error(f'Integrity error creating user: {e}')
            flash("Username or email already taken", "error")
            return redirect(url_for('auth.create_user'))

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error creating user: {e}')
            flash(f'Error creating user', "error")
            return redirect(url_for('auth.create_user'))

    # Render the create user form
    return render_template('auth/create_user.html')

@auth_bp.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.options(joinedload(User.updated_by)).get_or_404(user_id)
    if request.method == 'POST':

        # Check if the username is already taken
        existing_username = User.query.filter(
            User.username == request.form['username'],
            User.id != user_id
        ).first()
        if existing_username:
            current_app.logger.error(f'Username already taken for user {user_id}')
            flash('Username already taken', "error")
            return redirect(url_for('auth.user_list'))

        # Check if the email is already taken
        existing_email = User.query.filter(
            User.email == request.form['email'],
            User.id != user_id
        ).first()
        if existing_email:
            current_app.logger.error(f'Email already taken for user {user_id}')
            flash('Email already taken', "error")
            return redirect(url_for('auth.user_list'))

        try:
            user.username = request.form['username']
            user.email = request.form['email']
            user.is_admin = bool(request.form.get('is_admin'))
            if request.form['password']:
                user.password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
            user.updated_by_id = current_user.id
            user.updated_datetime = datetime.now(timezone.utc)
            db.session.commit()
            flash('User updated successfully', "success")
            return redirect(url_for('auth.user_list'))
        
        except IntegrityError as e:
            db.session.rollback()
            current_app.logger.error(f'Integrity error updating user {user_id}: {e}')
            flash("Username or email already taken", "error")
            return redirect(url_for('auth.user_list'))
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error updating user: {e}')
            flash("Error updating user", "error")
            return redirect(url_for('auth.user_list'))
    
    return render_template('auth/edit_user.html', user=user)

@auth_bp.route('/delete_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    try:
        user.active = False
        user.updated_by_id = current_user.id
        user.updated_datetime = datetime.now(timezone.utc)
        db.session.commit()
        flash('User deactivated successfully', "success")
        return redirect(url_for('auth.user_list'))
    
    except IntegrityError as e:
        db.session.rollback()
        current_app.logger.error(f'Integrity error deactivating user {user_id}: {e}')
        flash("Error deactivating user", "error")
        return redirect(url_for('auth.user_list'))
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error deactivating user {user_id}: {e}')
        flash("Error deactivating user", "error")
        return redirect(url_for('auth.user_list'))

@auth_bp.route('/reactivate_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def reactivate_user(user_id):
    user = User.query.get_or_404(user_id)
    try:
        user.active = True
        user.updated_by_id = current_user.id
        user.updated_datetime = datetime.now(timezone.utc)
        db.session.commit()
        flash('User reactivated successfully', "success")
        return render_template('auth/edit_user.html', user=user)

    except IntegrityError as e:
        db.session.rollback()
        current_app.logger.error(f'Integrity error reactivating user {user_id}: {e}')
        flash("Error reactivating user", "error")
        return redirect(url_for('auth.user_list'))
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error reactivating user {user_id}: {e}')
        flash("Error reactivating user", "error")
        return redirect(url_for('auth.user_list'))


@auth_bp.route('/user_list')
@login_required
@admin_required
def user_list():
    users_list = User.query.options(joinedload(User.updated_by)).order_by(User.username.asc()).all()
    return render_template('auth/user_list.html', users_list=users_list)