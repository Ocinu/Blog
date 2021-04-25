from flask_login import UserMixin
from sqlalchemy import func

from sweater import db, manager


@manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    access_rights = db.Column(db.Integer, default=1)
    name = db.Column(db.String(50), nullable=True)
    slug = db.Column(db.String(200), default='')
    email = db.Column(db.String(50), nullable=True, unique=True)
    phone = db.Column(db.String(20), nullable=True)
    avatar = db.Column(db.String(50), default='')
    post_number = db.Column(db.Integer, default=0)
    login = db.Column(db.String(30), nullable=False, unique=True)
    password = db.Column(db.String(120), nullable=False)
    registration_date = db.Column(db.DateTime(timezone=True), default=func.now())

    articles = db.relationship('Article', backref='author')

    def __repr__(self):
        return f'{self.id}, {self.login}'


tags = db.Table('tags',
                db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True),
                db.Column('article_id', db.Integer, db.ForeignKey('article.id'), primary_key=True)
                )


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    category_id = db.Column(db.Integer(), db.ForeignKey('category.id'))
    tags = db.relationship('Tag', secondary=tags, lazy='subquery',
                           backref=db.backref('articles', lazy=True))
    title = db.Column(db.String(100), nullable=False)
    text = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(50), default='')
    created_on = db.Column(db.DateTime(), default=func.now())
    updated_on = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    likes_count = db.Column(db.Integer, default=0)
    views = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'{self.id}, {self.title[:10]}'


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(50), nullable=True, unique=True)
    created_on = db.Column(db.DateTime(), default=func.now())
    articles = db.relationship('Article', backref='category')

    def __repr__(self):
        return {self.category_name}


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag_name = db.Column(db.String(50), nullable=True, unique=True)
    created_on = db.Column(db.DateTime(), default=func.now())

    def __repr__(self):
        return {self.tag_name}


class Likes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer(), db.ForeignKey('article.id'))
    date = db.Column(db.DateTime(), default=func.now())

    def __repr__(self):
        return self.post_id


db.create_all()
