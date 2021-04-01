import os
import random
import re
import string
from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash

from sweater import db, app
from sweater.database import Item, User

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class NewArticle:
    def __init__(self, author, title, text, image):
        self.errors = ''
        self.author = author
        self.title = title
        self.text = text
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
        self.articles = Item.query.all()

    @staticmethod
    def save_db(item):
        try:
            db.session.add(item)
            db.session.commit()
        except:
            return 'Ошибка записи в базу данных'

    def add_new_post(self, author, title, text, image):
        article = NewArticle(author, title, text, image)

        if len(article.errors) > 0:
            return str(article.errors)
        else:
            item = Item(author=article.author,
                        title=article.title,
                        text=article.text,
                        date=article.date,
                        image=article.image)
            self.save_db(item)
            self.articles = Item.query.all()
            return self.articles

    def update_articles(self):
        self.articles = Item.query.all()
        return self.articles

    def delete_article(self, article_id):
        try:
            item = Item.query.get(article_id)
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], item.image))
            db.session.delete(item)
            db.session.commit()
            self.articles = Item.query.all()
            return self.articles
        except:
            return 'Запись не найдена'

    def edit_article(self, author, title, text, image, article_id):
        # валидация полученных данных перед внесением изменений
        article = NewArticle(author, title, text, image)

        if len(article.errors) > 0:
            return str(article.errors)
        else:
            item = Item.query.get(article_id)
            item.author = article.author  # строка оставлена для администрирования
            item.title = article.title
            item.text = article.text
            # удаление старого файла
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], item.image))
            item.image = article.image
            self.save_db(item)
            self.articles = Item.query.all()
            return self.articles

    def update_views_count(self, article_id: int):
        item = Item.query.get(article_id)
        item.views += 1
        self.save_db(item)
        return item

    def update_likes_count(self, article_id: int):
        item = Item.query.get(article_id)
        item.likes += 1
        self.save_db(item)
        return item

    @staticmethod
    def get_article(article_id: int):
        item = Item.query.get(article_id)
        return item

    def sort_by_date(self):
        self.articles = Item.query.order_by(Item.date).all()
        return self.articles

    def sort_by_author(self):
        self.articles = Item.query.order_by(Item.author).all()
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
        new_user = User(name=self.name,
                        email=self.email,
                        phone=self.phone,
                        avatar=self.avatar,
                        login=self.login,
                        password=self.password)
        try:
            db.session.add(new_user)
            db.session.commit()
        except Exception as e:
            print(e)
        avatar.save(os.path.join(app.config['UPLOAD_FOLDER'], self.avatar))
        return True
