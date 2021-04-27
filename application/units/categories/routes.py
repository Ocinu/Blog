from flask import render_template, redirect, url_for, request
from flask_login import current_user

from application.units.articles.controller import LikesController, PostController
from application.units.categories.controller import CategoriesTotal, CategoryController, NewCategory


class CategoryRoutes:
    def __init__(self, app):
        self.app = app
        self.likes = LikesController()
        self.params = {
            'user': current_user,
            'errors': {}
        }

        @app.route('/category/<int:category_id>', methods=['POST', 'GET'])
        def category(category_id):
            categories = CategoriesTotal().categories
            self.params['categories'] = categories

            sort_by_category = CategoryController(category_id).category
            self.params['articles'] = sort_by_category.articles
            self.params['title'] = 'ItStep Blog: ' + sort_by_category.category_name

            self.params['likes_count'] = self.likes.checking_likes()

            return render_template('index.html', **self.params)

        @app.route('/add_category', methods=['POST'])
        def add_category():
            NewCategory(**request.form).add_new_category()
            return redirect(url_for('admin'))

        @app.route('/delete_category/<int:category_id>')
        def delete_category(category_id):
            item = CategoryController(category_id)
            item.delete_category()
            for i in item.category.articles:
                PostController(i.id).delete_post()
            return redirect(url_for('admin'))
