import os

from flask_login import current_user
from sqlalchemy import desc

from app import app
from application.models import ValidateImage, Tags, Articles, Likes, ControlDB
from application.units.tags.controller import NewTag
from application.units.users.controller import UserController


class ValidatePostData(ValidateImage):
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


class NewPost(ValidatePostData):
    def __init__(self, category_id: int, title: str, tags: str, text: str, article_image):
        super().__init__()
        self.author_id = current_user.id
        self.category_id = category_id
        self.title = title
        self.tags = tags
        self.text = text
        self.image = article_image

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

    def add_new_article(self, article_image):
        new_article = Articles()
        new_article.author_id = self.author_id
        new_article.category_id = self.category_id
        new_article.title = self.title
        new_article.text = self.text
        new_article.image = self.image

        self.save_new_tags()
        new_article.tags = self.add_tags(new_article)

        if len(self.errors) == 0:
            new_article_author = UserController(self.author_id).user
            new_article_author.post_number += 1
            self.save_to_db(new_article_author)
            if self.save_to_db(new_article):
                article_image.save(os.path.join(app.config['UPLOAD_FOLDER'], self.image))
        return True

    def save_new_tags(self):
        all_tags = Tags.query.all()
        all_tags = [i.tag_name for i in all_tags]
        for i in self.tags:
            if i not in all_tags:
                new_tag = NewTag(i)
                new_tag.save_tag()

    def add_tags(self, new_article):
        for i in self.tags:
            tag = Tags.query.filter_by(tag_name=i).first()
            new_article.tags.append(tag)
        return new_article.tags


class PostController(ValidatePostData):
    def __init__(self, post_id: int):
        super().__init__()
        self.post = Articles.query.get(post_id)

    def delete_post(self):
        self.post.author.post_number -= 1
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], self.post.image))
        LikesController().delete_likes(self.post.id)
        self.delete_from_db(self.post)
        return True

    def edit_post(self, title, tags, text, category_id, article_image):
        self.post.title = self.check_title(title)
        self.post.text = self.check_text(text)
        self.post.category_id = category_id

        tags = self.check_tags(tags)
        all_tags = Tags.query.all()
        all_tags = [i.tag_name for i in all_tags]
        for i in tags:
            if i not in all_tags:
                new_tag = NewTag(i)
                new_tag.save_tag()
        for i in tags:
            tag = Tags.query.filter_by(tag_name=i).first()
            if tag not in self.post.tags:
                self.post.tags.append(tag)
        # если поле пустое, оставляем старую картинку
        if article_image.filename != '':
            temp = self.post.image
            self.post.image = self.check_image(article_image)
            # если нет ошибок, удаляем старую картинку и сохраняем новую
            if len(self.errors) == 0:
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], temp))
                article_image.save(os.path.join(app.config['UPLOAD_FOLDER'], self.post.image))
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


class PostsTotal:
    def __init__(self):
        self.articles = Articles.query.all()

    def sort_by_date(self):
        self.articles = Articles.query.order_by(desc(Articles.created_on)).all()
        return self.articles

    def sort_by_author(self):
        self.articles = Articles.query.order_by(Articles.author_id).all()
        return self.articles


class LikesController(ControlDB):
    def __init__(self):
        super().__init__()
        self.num_likes = 0
        self.likes_check = []
        self.likes = Likes.query.all()
        self.check = None

    def checking_likes(self):
        try:
            self.likes_check = [i.post_id for i in Likes.query.filter_by(user_id=current_user.id).all()]
        except Exception as e:
            print(e)
        return self.likes_check

    def likes_number(self, user_id: int):
        try:
            self.num_likes = len(Likes.query.filter_by(user_id=user_id).all())
        except Exception as e:
            print(e)
        return str(self.num_likes)

    def delete_likes(self, post_id):
        delete_likes = Likes.query.filter_by(post_id=post_id).all()
        for i in delete_likes:
            self.delete_from_db(i)

    def add_like(self, post_id):
        self.check = [i.post_id for i in Likes.query.filter_by(user_id=current_user.id).all()]
        if post_id not in self.check:
            PostController(post_id).update_likes_count(post_id, current_user.id)
            return True
        return False
