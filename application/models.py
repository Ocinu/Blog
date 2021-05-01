import random
import string

from flask_login import UserMixin
from sqlalchemy import func

from app import db


# database tables
class Users(db.Model, UserMixin):
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

    articles = db.relationship('Articles', backref='author')

    def __repr__(self):
        return f'{self.id}, {self.login}'


tags = db.Table('tags_glue',
                db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True),
                db.Column('article_id', db.Integer, db.ForeignKey('articles.id'), primary_key=True)
                )


class Articles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer(), db.ForeignKey('users.id'))
    category_id = db.Column(db.Integer(), db.ForeignKey('categories.id'))
    tags = db.relationship('Tags', secondary=tags, lazy='subquery',
                           backref=db.backref('articles', lazy=True))
    title = db.Column(db.String(100), nullable=False)
    text = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(50), default='')
    created_on = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_on = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    likes_count = db.Column(db.Integer, default=0)
    views = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'{self.id}, {self.title[:10]}'


class Categories(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(50), nullable=True, unique=True)
    created_on = db.Column(db.DateTime(timezone=True), default=func.now())
    articles = db.relationship('Articles', backref='category')

    def __repr__(self):
        return {self.category_name}


class Tags(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag_name = db.Column(db.String(50), nullable=True, unique=True)
    created_on = db.Column(db.DateTime(timezone=True), default=func.now())

    def __repr__(self):
        return {self.tag_name}


class Likes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer(), db.ForeignKey('articles.id'))
    date = db.Column(db.DateTime(timezone=True), default=func.now())

    def __repr__(self):
        return self.post_id


class Visitors(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(), nullable=False)
    visit_datetime = db.Column(db.DateTime(timezone=True), default=func.now())
    visit_page = db.Column(db.String())

    def __repr__(self):
        return self.ip_address


# parent classes
class Errors:
    def __init__(self):
        self.errors = {}


class ControlDB(Errors):
    def __init__(self):
        super().__init__()

    def save_to_db(self, item):
        try:
            db.session.add(item)
            db.session.commit()
            return True
        except Exception as e:
            self.errors['db_error'] = str(e)
            return False

    def delete_from_db(self, item):
        try:
            db.session.delete(item)
            db.session.commit()
            return True
        except Exception as e:
            self.errors['db_error'] = str(e)
            return False


class ValidateImage(ControlDB):
    def __init__(self):
        self.ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
        super().__init__()

    def allowed_file(self, filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS

    def check_image(self, value):
        if self.allowed_file(value.filename):
            random_name = ''.join([random.choice(string.digits + string.ascii_letters) for x in range(10)])
            img_path = f'sweater/static/images/{random_name}.jpg'
            image_name = str(img_path.split('/')[-1:])[2:-2]
            return image_name
        self.errors['image_error'] = "Допустимые расширения файла: 'png', 'jpg', 'jpeg', 'gif' \n"
        return ''


db.create_all()
