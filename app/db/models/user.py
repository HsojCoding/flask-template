from app.db import db
from datetime import datetime, timezone

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    is_admin = db.Column(db.Boolean, default=False)
    active = db.Column(db.Boolean, default=True)

    updated_datetime = db.Column(
        db.DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
        nullable=False
    )

    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    updated_by = db.relationship('User', backref='updated_users', remote_side=[id])

    def __repr__(self):
        return f"<User {self.username}>"