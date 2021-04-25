import os
import random
import re
import string

from sqlalchemy import desc
from werkzeug.security import generate_password_hash, check_password_hash

from sweater import db, app
from sweater.models import Article, User, Category, Tag, Likes


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
        except:
            self.errors['db_error'] = 'Database write error'
            return False

    def delete_from_db(self, item):
        try:
            db.session.delete(item)
            db.session.commit()
            return True
        except:
            self.errors['db_error'] = 'Database write error'
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


class ValidateUserdata(ValidateImage):
    def __init__(self):
        super().__init__()

    def check_login(self, value: str):
        value = value.strip()
        if 4 < len(value) < 30:
            return value
        self.errors['login_error'] = 'От 5 до 30 символов'
        return value

    def check_name(self, value: str):
        if isinstance(value, str):
            #  убираем лишние пробелы
            value = ' '.join([x for x in value.split(' ') if x != ''])
            if 1 <= len(value.split(' ')) <= 3:
                return value
            self.errors['name_error'] = 'В имени неможет быть больше 3-х слов и меньше 1'
            return value
        self.errors['name_error'] = 'This is not a string'
        return value

    def check_email(self, value: str):
        if re.search(r'(\w+@[a-zA-Z_]+?\.[a-zA-Z]{2,6})', str(value)):
            return value
        self.errors['mail_error'] = 'Введите корректный электронный адрес'
        return ''

    def check_slug(self, value: str):
        #  убираем лишние пробелы
        value = ' '.join([x for x in value.split(' ') if x != ''])
        if isinstance(value, str):
            if 10 <= len(value) <= 200:
                return value
            self.errors['slug_error'] = 'From 10 to 200 characters'
            return value
        self.errors['slug_error'] = 'This is not a string'
        return value

    def check_phone(self, value):
        if re.search(r'^\+\d{12}$', str(value)):
            return value
        self.errors['phone_error'] = 'Введите номер телефона в формате +380999999999\n'
        return value

    def check_password_strength(self, value: str):
        if re.search(r'((?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,15})', str(value)):
            hash_pwd = generate_password_hash(value)
            return hash_pwd
        self.errors['password_error'] = ('Пароль должен содержать от 8 до 15 символов '
                                         'должна быть минимум одна заглавная буква '
                                         'должна быть минимум одна прописная буква '
                                         'должна быть минимум одна цыфра')
        return ''


class ValidateArticleData(ValidateImage):
    def __init__(self):
        super().__init__()

    def check_title(self, value: str):
        if value != '':
            if isinstance(value, str):
                if len(value) < 100:
                    return value
                self.errors['title_error'] = '5 to 30 characters'
                return value
            self.errors['title_error'] = 'Title must be a string'
            return value
        self.errors['title_error'] = 'The field cannot be empty'
        return value

    def check_text(self, value: str):
        if isinstance(value, str):
            if len(value) > 130:
                return value
            self.errors['text_error'] = 'The text is too short (from 130 characters)'
            return value
        self.errors['text_error'] = 'Title must be a string'
        return value

    def check_tags(self, value: str):
        if isinstance(value, str):
            # убираем лишние пробелы
            value = [x for x in value.split(' ') if x != '']
            # убираем запятые в конце тэгов
            for e, i in enumerate(value):
                if i[-1] == ',':
                    value[e] = i[:-1]
            return value
        self.errors['tags_error'] = 'Must be a string'
        return value


class NewUser(ValidateUserdata):
    def __init__(self, name, email, slug, phone, avatar, login, password, password2):
        super().__init__()
        self.name = name
        self.email = email
        self.slug = slug
        self.phone = phone
        self.avatar = avatar
        self.login = login
        self.password = password
        self.password2 = password2
        self.check_password()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value: str):
        value = self.check_name(value)
        self._name = value

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value: str):
        #  проверка на уникальность email
        exist_email = User.query.filter_by(email=value).all()
        if exist_email:
            self.errors['mail_error'] = 'Такой электронный адрес уже зарегистрирован\n'
            self._email = value
        else:
            value = self.check_email(value)
            self._email = value

    @property
    def slug(self):
        return self._slug

    @slug.setter
    def slug(self, value: str):
        self._slug = self.check_slug(value)

    @property
    def phone(self):
        return self._phone

    @phone.setter
    def phone(self, value):
        value = self.check_phone(value)
        self._phone = value

    @property
    def avatar(self):
        return self._avatar

    @avatar.setter
    def avatar(self, value):
        self._avatar = self.check_image(value)

    @property
    def login(self):
        return self._login

    @login.setter
    def login(self, value: str):
        #  проверка на уникальность логина
        exist_user = User.query.filter_by(login=value).all()
        if exist_user:
            self.errors['login_error'] = 'Пользователь с таким логином уже зарегестрирован'
            self._login = ''
        else:
            value = self.check_login(value)
            self._login = value

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        value = self.check_password_strength(value)
        self._password = value

    def check_password(self):
        if check_password_hash(self.password, self.password2):
            return True
        self.errors['password_error'] = 'Passwords not equal'
        return False

    def add_new_user(self, avatar):
        new_user = User()
        new_user.name = self.name
        new_user.slug = self.slug
        new_user.email = self.email
        new_user.phone = self.phone
        new_user.avatar = self.avatar
        new_user.login = self.login
        new_user.password = self.password

        if len(self.errors) == 0:
            if self.save_to_db(new_user):
                avatar.save(os.path.join(app.config['UPLOAD_FOLDER'], self.avatar))
        return True


class Author(ValidateUserdata):
    def __init__(self, user_id: int):
        super().__init__()
        self.user = user_id

    @property
    def user(self):
        return self._user_id

    @user.setter
    def user(self, value: int):
        self._user_id = User.query.get(value)

    def check_password(self, password):
        if check_password_hash(self.user.password, password):
            return True
        else:
            self.errors['password_error'] = 'Password incorrect'
            return False

    def edit_info(self, login, name, slug, email, phone, avatar):
        self.user.login = self.check_login(login)
        self.user.name = self.check_name(name)
        self.user.slug = self.check_slug(slug)
        self.user.email = self.check_email(email)
        self.user.phone = self.check_phone(phone)

        if avatar.filename != '':
            temp = self.user.avatar
            self.user.avatar = self.check_image(avatar)
            # если нет ошибок, удаляем старую картинку и сохраняем новую
            if len(self.errors) == 0:
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], temp))
                avatar.save(os.path.join(app.config['UPLOAD_FOLDER'], self.user.avatar))
                self.save_to_db(self.user)

        if len(self.errors) == 0:
            self.save_to_db(self.user)
            return True
        return False

    def edit_slug(self, slug):
        self.user.slug = self.check_slug(slug)
        if len(self.errors) == 0:
            self.save_to_db(self.user)
            return True
        return False

    def edit_password(self, new_password, new_password2):
        if new_password != new_password2:
            self.errors['password_error'] = 'New passwords are not equal'
            return False
        self.user.password = self.check_password_strength(new_password)
        if len(self.errors) == 0:
            self.save_to_db(self.user)
            return True
        return False

    def delete_user(self):
        # удаление аватарки
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], self.user.avatar))
        # удаление всех постов автора
        for post in self.user.articles:
            Post(post.id).delete_post()
        self.delete_from_db(self.user)


class NewArticle(ValidateArticleData):
    def __init__(self, author_id: int, category_id: int, title: str, tags: str, text: str, image):
        super().__init__()
        self.author_id = author_id
        self.category_id = category_id
        self.title = title
        self.tags = tags
        self.text = text
        self.image = image

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value: str):
        self._title = self.check_title(value)

    @property
    def tags(self):
        return self._tags

    @tags.setter
    def tags(self, value: str):
        self._tags = self.check_tags(value)

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value: str):
        self._text = self.check_text(value)

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, value):
        self._image = self.check_image(value)

    def add_new_article(self, image):
        new_article = Article()
        new_article.author_id = self.author_id
        new_article.category_id = self.category_id
        new_article.title = self.title
        new_article.text = self.text
        new_article.image = self.image

        self.save_new_tags()
        new_article.tags = self.add_tags(new_article)

        if len(self.errors) == 0:
            new_article_author = Author(self.author_id).user
            new_article_author.post_number += 1
            self.save_to_db(new_article_author)
            if self.save_to_db(new_article):
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], self.image))
        return True

    def save_new_tags(self):
        all_tags = Tag.query.all()
        all_tags = [i.tag_name for i in all_tags]
        for i in self.tags:
            if i not in all_tags:
                new_tag = NewTag(i)
                new_tag.save_tag()

    def add_tags(self, new_article):
        for i in self.tags:
            tag = Tag.query.filter_by(tag_name=i).first()
            new_article.tags.append(tag)
        return new_article.tags


class Post(ValidateArticleData):
    def __init__(self, post_id: int):
        super().__init__()
        self.post = Article.query.get(post_id)

    def delete_post(self):
        self.post.author.post_number -= 1
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], self.post.image))
        self.delete_from_db(self.post)
        return True

    def edit_post(self, title, tags, text, category_id, image):
        self.post.title = self.check_title(title)
        self.post.text = self.check_text(text)
        self.post.category_id = category_id

        tags = self.check_tags(tags)
        all_tags = Tag.query.all()
        all_tags = [i.tag_name for i in all_tags]
        for i in tags:
            if i not in all_tags:
                new_tag = NewTag(i)
                new_tag.save_tag()
        for i in tags:
            tag = Tag.query.filter_by(tag_name=i).first()
            if tag not in self.post.tags:
                self.post.tags.append(tag)
        # если поле пустое, оставляем старую картинку
        if image.filename != '':
            temp = self.post.image
            self.post.image = self.check_image(image)
            # если нет ошибок, удаляем старую картинку и сохраняем новую
            if len(self.errors) == 0:
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], temp))
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], self.post.image))
                self.save_to_db(self.post)

        if len(self.errors) == 0:
            self.save_to_db(self.post)
            return True
        return False

    def delete_tag(self, tag_id):
        for i in self.post.tags:
            if i.id == tag_id:
                self.post.tags.remove(i)
                self.save_to_db(self.post)
        return True

    def update_views_count(self):
        self.post.views += 1
        self.save_to_db(self.post)
        return True

    def update_likes_count(self, post_id: int, user_id: int):
        like = Likes(post_id=post_id, user_id=user_id)
        self.save_to_db(like)
        self.post.likes_count += 1
        self.save_to_db(self.post)
        return True


class NewTag(ValidateArticleData):
    def __init__(self, tag_name):
        super().__init__()
        self.tag_name = tag_name

    @property
    def tag_name(self):
        return self._tag_name

    @tag_name.setter
    def tag_name(self, value: str):
        self._tag_name = value

    def save_tag(self):
        new_tag = Tag()
        new_tag.tag_name = self.tag_name
        if self.save_to_db(new_tag):
            return True
        return False


class TagController:
    def __init__(self, tag_id):
        self.tag = Tag.query.get(tag_id)


class Articles:
    def __init__(self):
        self.articles = Article.query.all()

    def sort_by_date(self,):
        self.articles = Article.query.order_by(desc(Article.created_on)).all()
        return self.articles

    def sort_by_author(self):
        self.articles = Article.query.order_by(Article.author_id).all()
        return self.articles
