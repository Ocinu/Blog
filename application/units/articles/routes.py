from flask import render_template, request, redirect, abort, url_for
from flask_login import current_user, login_required

from application.units.articles.controller import NewPost, PostController, LikesController
from application.units.categories.controller import CategoriesTotal


class ArticleRoutes:
    def __init__(self, app):
        self.app = app
        self.params = {
            'user': current_user,
            'errors': {},
            'title': 'New post',
            'categories': CategoriesTotal().categories,
        }

        @app.route('/article/<int:post_id>')
        def article(post_id):
            post_model = PostController(post_id)
            post_model.update_views_count()

            full_info = post_model.post
            self.params['title'] = 'PostsTotal: ' + full_info.title
            self.params['article'] = full_info

            return render_template('articles/article.html', **self.params)

        @app.route('/new_article', methods=['POST', 'GET'])
        @login_required
        def new_article():
            self.params['check'] = True
            if request.method == 'POST':
                new_post = NewPost(**request.form, **request.files)

                self.params['check'] = False
                self.params['errors'] = new_post.errors
                self.params['edit_info'] = new_post

                if len(new_post.errors) > 0:
                    return render_template('articles/new_post.html', **self.params)
                new_post.add_new_article(**request.files)
                return redirect('/')
            return render_template('articles/new_post.html', **self.params)

        @app.route('/edit/<int:post_id>', methods=['POST', 'GET'])
        @login_required
        def edit_article(post_id):
            edit_model = PostController(post_id)
            edit_info = edit_model.post
            self.params['title'] = 'Edit article:' + edit_info.title
            self.params['edit_info'] = edit_info

            if request.method == 'POST':
                edit_model.edit_post(**request.files, **request.form)
                self.params['errors'] = edit_model.errors

                if len(edit_model.errors) == 0:
                    return redirect('/')
                return render_template('articles/edit_post.html', **self.params)
            return render_template('articles/edit_post.html', **self.params)

        @app.route('/delete/<int:post_id>')
        @login_required
        def delete_article(post_id):
            PostController(post_id).delete_post()
            return redirect('/')

        @app.route('/like/<int:post_id>')
        @login_required
        def add_like(post_id):
            if LikesController().add_like(post_id):
                return redirect(request.referrer or url_for('main'))
            abort(404)
