import os
import random
import re
import string
from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash

from sweater import db, app
from sweater.models import Article, User, Category, Tag, Likes

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class NewArticle:
    def __init__(self, author_id, title, text, image, category_id, tags):
        self.errors = ''
        self.author_id = author_id
        self.title = title
        self.text = text
        self.category_id = category_id
        # self.tag = 'tag'
        self.tags = tags
        self.date = datetime.strftime(datetime.now(), '%Y-%m-%d')
        self.image = image

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value: str):
        if value != '':
            if isinstance(value, str):
                if len(value) < 100:
                    self._title = value
                else:
                    error = 'Название слишком длинное (до 100 символов)\n'
                    self.add_error(error)
                    self._title = ''
            else:
                error = 'Название должно быть строкой\n'
                self.add_error(error)
                self._title = ''
        else:
            error = 'Поле неможет быть пустым\n'
            self.add_error(error)
            self._title = ''

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value: str):
        if isinstance(value, str):
            if len(value) > 130:
                self._text = value
            else:
                error = 'Текст слишком короткий (от 130 символов)\n'
                self.add_error(error)
                self._text = ''
        else:
            error = 'Текст должен быть строкой\n'
            self.add_error(error)
            self._text = ''

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, value):
        if value == '':
            error = 'Файл не выбран\n'
            self.add_error(error)
            self._image = ''
        elif value and allowed_file(value.filename):
            # filename = secure_filename(value.filename)
            random_name = ''.join([random.choice(string.digits + string.ascii_letters) for x in range(10)])
            img_path = f'sweater/static/images/{random_name}.jpg'

            try:
                # value.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                value.save(img_path)
            except Exception as e:
                print(e)

            self._image = str(img_path.split('/')[-1:])[2:-2]
            # self._image = filename

        else:
            error = 'Неверное расширение файла\n'
            self.add_error(error)
            self._image = ''

    def add_error(self, error):
        self.errors = self.errors + error
        return self.errors


class Articles:
    def __init__(self):
        self.articles = Article.query.all()

    @staticmethod
    def save_db(item):
        try:
            db.session.add(item)
            db.session.commit()
        except:
            return 'Ошибка записи в базу данных'

    def add_new_post(self, author_id, title, text, image, category_id, tags=1):
        article = NewArticle(author_id, title, text, image, category_id, tags)
        # category = Category()

        if len(article.errors) > 0:
            return str(article.errors)
        else:
            user = User.query.get(1)
            post = Article.query.get(2)

            item = Article(
                # author=article.author,
                author_id=article.author_id,
                title=article.title,
                text=article.text,
                category_id=article.category_id,
                # tag=tag.tag_name,
                created_on=article.date,
                image=article.image
            )
            post = Article.query.get(2)

            self.save_db(item)
            self.articles = Article.query.all()

            tag = Tag.query.all()
            # db.session.add(tag)
            # db.session.commit()
            return self.articles

    def update_articles(self):
        self.articles = Article.query.all()
        return self.articles

    def delete_article(self, article_id):
        try:
            item = Article.query.get(article_id)
            item.author.post_number -= 1
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], item.image))
            db.session.delete(item)
            db.session.commit()
            self.articles = Article.query.all()
            return self.articles
        except:
            return 'Запись не найдена'

    def edit_article(self, author, title, text, image, article_id):
        # валидация полученных данных перед внесением изменений
        article = NewArticle(author, title, text, image)

        if len(article.errors) > 0:
            return str(article.errors)
        else:
            item = Article.query.get(article_id)
            item.author = article.author  # строка оставлена для администрирования
            item.title = article.title
            item.text = article.text
            # удаление старого файла
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], item.image))
            item.image = article.image
            self.save_db(item)
            self.articles = Article.query.all()
            return self.articles

    def update_views_count(self, article_id: int):
        item = Article.query.get(article_id)
        item.views += 1
        self.save_db(item)
        return item

    def update_likes_count(self, article_id: int, user_id: int):
        like = Likes(post_id=article_id, user_id=user_id)
        self.save_db(like)
        item = Article.query.get(article_id)
        item.likes_count += 1
        self.save_db(item)
        return item

    @staticmethod
    def get_article(article_id: int):
        item = Article.query.get(article_id)
        return item

    def sort_by_date(self):
        self.articles = Article.query.order_by(Article.created_on).all()
        return self.articles

    def sort_by_author(self):
        self.articles = Article.query.order_by(Article.author_id).all()
        return self.articles


class NewUser:
    def __init__(self, name, email, phone, avatar, login, password, password2):
        self.errors = ''
        self.name = name
        self.email = email
        self.phone = phone
        self.avatar = avatar
        self.registration_date = datetime.strftime(datetime.now(), '%Y-%m-%d')
        self.login = login
        self.password = password
        self.password2 = password2
        self.check_password()

    def add_error(self, error):
        self.errors = self.errors + error
        return self.errors

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value: str):
        if isinstance(value, str):
            #  убираем лишние пробелы
            value = ' '.join([x for x in value.split(' ') if x != ''])
            if len(value.split(' ')) <= 3:
                self._name = value
            else:
                error = 'В имени неможет быть больше 3-х слов\n'
                self.add_error(error)
                self._text = ''
        else:
            error = 'Имя должно быть строкой\n'
            self.add_error(error)
            self._text = ''

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value: str):
        #  проверка на уникальность email
        exist_email = User.query.filter_by(email=value).all()
        if exist_email:
            error = 'Такой электронный адрес уже зарегистрирован\n'
            self.add_error(error)
            self._email = ''
        else:
            if re.search(r'(\w+@[a-zA-Z_]+?\.[a-zA-Z]{2,6})', str(value)):
                self._email = value
            else:
                error = 'Введите корректный электронный адрес\n'
                self.add_error(error)
                self._email = ''

    @property
    def phone(self):
        return self._phone

    @phone.setter
    def phone(self, value):
        if re.search(r'^\+\d{12}$', str(value)):
            self._phone = value
        else:
            error = 'Введите номер телефона в формате +380999999999\n'
            self.add_error(error)
            self._phone = ''

    @property
    def avatar(self):
        return self._avatar

    @avatar.setter
    def avatar(self, value):
        if allowed_file(value.filename):
            random_name = ''.join([random.choice(string.digits + string.ascii_letters) for x in range(10)])
            img_path = f'sweater/static/images/{random_name}.jpg'
            # value.save(img_path)
            self._avatar = str(img_path.split('/')[-1:])[2:-2]
        else:
            error = "Допустимые расширения файла: 'png', 'jpg', 'jpeg', 'gif' \n"
            self.add_error(error)
            self._avatar = ''

    @property
    def login(self):
        return self._login

    @login.setter
    def login(self, value: str):
        value = value.strip()
        #  проверка на уникальность логина
        exist_user = User.query.filter_by(login=value).all()
        if exist_user:
            error = 'Пользователь с таким логином уже зарегестрирован\n'
            self.add_error(error)
            self._login = ''
        else:
            if 4 < len(value) < 30:
                self._login = value
            else:
                error = 'От 5 до 30 символов\n'
                self.add_error(error)
                self._login = ''

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        if re.search(r'((?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,15})', str(value)):
            hash_pwd = generate_password_hash(value)
            self._password = hash_pwd
        else:
            error = ('Пароль должен содержать от 8 до 15 символов'
                     'должна быть минимум одна заглавная буква'
                     'должна быть минимум одна прописная буква'
                     'должна быть минимум одна цыфра')
            self.add_error(error)
            self._password = ''

    def check_password(self):
        if check_password_hash(self.password, self.password2):
            return True
        else:
            error = 'Пароли не совпадают\n'
            self.add_error(error)
            return False

    def add_new_user(self, avatar):
        if len(self.errors) > 0:
            return self.errors
        new_user = User()
        new_user.name = self.name
        new_user.email = self.email
        new_user.phone = self.phone
        new_user.avatar = self.avatar
        new_user.registration_date = self.registration_date
        new_user.login = self.login
        new_user.password = self.password

        try:
            db.session.add(new_user)
            db.session.commit()
        except Exception as e:
            print(e)
        avatar.save(os.path.join(app.config['UPLOAD_FOLDER'], self.avatar))
        return True


class Author:
    def __init__(self, user_id: int):
        self.errors = ''
        self.user = user_id

    @property
    def user(self):
        return self._user_id

    @user.setter
    def user(self, value: int):
        self._user_id = User.query.get(value)

    def add_error(self, error):
        self.errors = self.errors + error
        return self.errors

    def check_password(self, password):
        if check_password_hash(self.user.password, password):
            return True
        else:
            error = 'Password incorrect\n'
            self.add_error(error)
            return False

    def save_db(self):
        db.session.add(self.user)
        db.session.commit()

    def edit_info(self, login, name, email, phone):
        self.edit_login(login)
        self.edit_name(name)
        self.edit_email(email)
        self.edit_phone(phone)
        return self.user

    def edit_login(self, value):
        value = value.strip()
        #  проверка на уникальность логина
        exist_user = User.query.filter_by(login=value).all()
        if exist_user and self.user.login != value:
            error = 'Пользователь с таким логином уже зарегестрирован\n'
            self.add_error(error)
            self.user.login = value
            return self.user.name
        else:
            if 4 < len(value) < 30:
                self.user.login = value
                return self.user.name
            else:
                error = 'От 5 до 30 символов\n'
                self.add_error(error)
                self.user.login = value
                return self.user.name

    def edit_name(self, value):
        if isinstance(value, str):
            #  убираем лишние пробелы
            value = ' '.join([x for x in value.split(' ') if x != ''])
            if len(value.split(' ')) <= 3:
                self.user.name = value
                return self.user.name
            else:
                error = 'В имени неможет быть больше 3-х слов\n'
                self.add_error(error)
                self.user.name = value
                return self.user.name
        else:
            error = 'Имя должно быть строкой\n'
            self.add_error(error)
            self.user.name = value
            return self.user.name

    def edit_email(self, value):
        #  проверка на уникальность email
        exist_email = User.query.filter_by(email=value).all()
        if exist_email and self.user.email != value:
            error = 'Такой электронный адрес уже зарегистрирован\n'
            self.add_error(error)
            self.user.email = value
            return self.user.email
        else:
            if re.search(r'(\w+@[a-zA-Z_]+?\.[a-zA-Z]{2,6})', str(value)):
                self.user.email = value
                return self.user.email
            else:
                error = 'Введите корректный электронный адрес\n'
                self.add_error(error)
                self.user.email = value
                return self.user.email

    def edit_phone(self, value):
        if re.search(r'^\+\d{12}$', str(value)):
            self.user.phone = value
            return self.user.phone
        else:
            error = 'Введите номер телефона в формате +380999999999\n'
            self.add_error(error)
            self.user.phone = value
            return self.user.phone
