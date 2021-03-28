from datetime import datetime

from sweater import db
from sweater.database import Item


class NewArticle:
    def __init__(self, author, title, text):
        self.id = None
        self.author = author
        self.title = title
        self.text = text
        self.date = datetime.strftime(datetime.now(), '%Y-%m-%d')
        self.likes = 0
        self.views = 0

    @property
    def author(self):
        return self._author

    @author.setter
    def author(self, value):
        self._author = value

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value


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

    def add_new_post(self, author, title, text):
        article = NewArticle(author, title, text)
        item = Item(author=article.author, title=article.title, text=article.text, date=article.date)
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

    @staticmethod
    def get_article(article_id: int):
        item = Item.query.get(article_id)
        return item
