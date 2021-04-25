import os
import re

from werkzeug.security import generate_password_hash, check_password_hash

from app import app
from application.models import ValidateImage, Users


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
            if 1 <= len(value.split(' ')) <= 3 and len(value) > 0:
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
        exist_email = Users.query.filter_by(email=value).all()
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
        exist_user = Users.query.filter_by(login=value).all()
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
        new_user = Users()
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


class UserController(ValidateUserdata):
    def __init__(self, user_id: int):
        super().__init__()
        self.user = user_id

    @property
    def user(self):
        return self._user_id

    @user.setter
    def user(self, value: int):
        self._user_id = Users.query.get(value)

    def check_password(self, password):
        if check_password_hash(self.user.password, password):
            return True
        else:
            self.errors['password_error'] = 'Password incorrect'
            return False

    def edit_info(self, login, name, slug, email, phone, avatar, **kwargs):
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
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], self.user.avatar))
        except Exception as e:
            print(e)
        self.delete_from_db(self.user)


class UsersTotal:
    def __init__(self):
        self.users = Users.query.all()
