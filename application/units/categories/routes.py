from flask import render_template
from flask_login import current_user

from application.units.articles.controller import LikesController
from application.units.categories.controller import CategoriesTotal, CategoryController


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
