from flask import render_template, redirect, url_for
from flask_login import current_user

from application.units.articles.controller import PostController, LikesController
from application.units.categories.controller import CategoriesTotal
from application.units.tags.controller import TagController


class TagRoutes:
    def __init__(self, app):
        self.app = app
        self.params = {
            'user': current_user,
            'errors': {},
            'edit_info': {}
        }

        @app.route('/tag/<int:tag_id>')
        def tag(tag_id):
            current_tag = TagController(tag_id).tag
            self.params['title'] = 'ItStep Blog: ' + current_tag.tag_name
            self.params['articles'] = current_tag.articles
            self.params['likes_count'] = LikesController().checking_likes()
            self.params['categories'] = CategoriesTotal().categories
            return render_template('index.html', **self.params)

        @app.route('/tag/delete/<int:post_id>/<int:tag_id>')
        def delete_tag_from_post(post_id, tag_id):
            PostController(post_id).delete_tag(tag_id)
            return redirect(f'/edit/{post_id}')

        @app.route('/delete_tag/<int:tag_id>')
        def delete_tag(tag_id):
            TagController(tag_id).delete_tag()
            return redirect(url_for('admin'))
