from flask_login import LoginManager, current_user
from flask_bcrypt import Bcrypt
from app.db.models import User
from functools import wraps
from flask import flash, redirect, url_for

login_manager = LoginManager()
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

bcrypt = Bcrypt()

def admin_required(f):
    """
    Decorator to check if a user is authenticated and is an admin.

    If the user is not authenticated, they are redirected to the login page.
    If the user is not an admin, they are redirected to the home page.
    Otherwise, the wrapped function is called as normal.

    It can be used independently of the login_required decorator,
    it is recommended to use it in conjunction with the login_required decorator
    so that any usual login_required checks are still performed.

    Example:
    @admin_required
    def create_user():
        return render_template('admin/create_user.html')
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('You must be logged in to access this page', 'error')
            return redirect(url_for('auth.login'))
        
        if not current_user.is_admin:
            flash('You are not authorized to access this page', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function