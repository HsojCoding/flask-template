from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from app.db.models import User

login_manager = LoginManager()
login_manager.login_view = 'auth_bp.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

bcrypt = Bcrypt()