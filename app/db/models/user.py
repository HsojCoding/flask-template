from app.db import db
from datetime import datetime, timezone
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    is_admin = db.Column(db.Boolean, default=False)
    active = db.Column(db.Boolean, default=True) # Is just a reverse deleted flag

    updated_datetime = db.Column(
        db.DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
        nullable=False
    )

    updated_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    updated_by = db.relationship('User', backref='updated_users', remote_side=[id])

    @property
    def is_active(self):
        return self.active # UserMixin override for flask-login

    def remove_sensitive_data(self):
        self.password = None
        return self

    def __repr__(self):
        return f"<User {self.username}>"