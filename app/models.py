from app import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import login


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(UserMixin, db.Model):
    # ...
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120))
    password = db.Column(db.String(80))
    downloads = db.relationship('Download', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.email)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Download(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Download {}>'.format(self.body)
