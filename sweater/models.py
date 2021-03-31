import os
import random
import string
from datetime import datetime

from werkzeug.utils import secure_filename

from sweater import db, app
from sweater.database import Item

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class NewArticle:
    def __init__(self, author, title, text, image):
        self.id = None
        self.errors = ''
        self.author = author
        self.title = title
        self.text = text
        self.date = datetime.strftime(datetime.now(), '%Y-%m-%d')
        self.likes = 0
        self.views = 0
        self.image = image

    # @property
    # def author(self):
    #     return self._author
    #
    # @author.setter
    # def author(self, value: str):
    #     if isinstance(value, str):
    #         if len(value.split(' ')) < 4 and value.split(' ')[-1] != '' and value.split(' ')[0] != '':
    #             self._author = value
    #         else:
    #             self.errors.append('В имени неможет быть больше 3-х слов')
    #     else:
    #         self.errors.append('Имя должно быть строкой')

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value: str):
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
            db.session.delete(item)
            db.session.commit()
            self.articles = Item.query.all()
            return self.articles
        except:
            return 'Запись не найдена'

    def edit_article(self, author, title, text, article_id):
        # валидация полученных данных перед внесением изменений
        article = NewArticle(author, title, text)
        item = Item.query.get(article_id)
        item.author = article.author
        item.title = article.title
        item.text = article.text
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
