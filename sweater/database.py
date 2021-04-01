from datetime import datetime

from flask_login import UserMixin

from sweater import db, manager


@manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    access_rights = db.Column(db.Integer, default=1)
    name = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(50), nullable=True, unique=True)
    phone = db.Column(db.String(20), nullable=True)
    avatar = db.Column(db.String(50), default='')
    post_number = db.Column(db.Integer, default=0)
    login = db.Column(db.String(30), nullable=False, unique=True)
    password = db.Column(db.String(120), nullable=False)
    registration_date = db.Column(db.DateTime(), default=datetime.utcnow)

    def __repr__(self):
        return self.login


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    text = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), default='')
    date = db.Column(db.Text, default='')
    likes = db.Column(db.Integer, default=0)
    views = db.Column(db.Integer, default=0)
    image = db.Column(db.String(50), default='')

    def __repr__(self):
        return self.title[:10]


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(50), nullable=True, unique=True)
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)


class Likes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=True)
    post_id = db.Column(db.Integer, nullable=True)
    date = db.Column(db.DateTime(), default=datetime.utcnow)

db.create_all()
