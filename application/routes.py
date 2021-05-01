from flask import render_template, request, redirect, flash, url_for, abort
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash

from application.models import Users

from application.units.articles.controller import PostsTotal, LikesController
from application.units.categories.controller import CategoriesTotal
from application.units.tags.controller import TagTotal
from application.units.users.controller import UsersTotal, Visit


class MainRoutes:
    def __init__(self, app, manager):
        self.app = app
        self.manager = manager
        self.params = {
            'title': 'ItStep Blog',
            'user': current_user,
            'errors': {},
            'edit_info': {}
        }

        @app.before_request
        def before_request():
            pass

        @app.after_request
        def redirect_to_signin(response):
            if response.status_code == 401:
                return redirect(url_for('login_page') + '?next=' + request.url)
            return response

        @app.route('/', methods=['POST', 'GET'])
        def main():
            self.params['likes_count'] = LikesController().checking_likes()
            self.params['categories'] = CategoriesTotal().categories
            Visit().add_visit('main')

            if request.method == 'POST':
                value = request.form['sort_by']
                if value == 'date':
                    self.params['articles'] = PostsTotal().sort_by_date()
                    return render_template('index.html', **self.params)
                else:
                    self.params['articles'] = PostsTotal().sort_by_author()
                    return render_template('index.html', **self.params)
            else:
                self.params['articles'] = PostsTotal().articles
                return render_template('index.html', **self.params)

        @app.route('/admin')
        @login_required
        def admin():
            if current_user.access_rights > 4:
                Visit().add_visit('admin')
                self.params['title'] = 'ItStep Blog: administration'
                self.params['authors'] = UsersTotal().users
                self.params['articles'] = PostsTotal().articles
                self.params['likes_count'] = LikesController().checking_likes()
                self.params['categories'] = CategoriesTotal().categories
                self.params['tags'] = TagTotal().tags
                self.params['statistic'] = Visit().get_statistics()

                return render_template('admin.html', **self.params)
            abort(403)

        @app.route('/about')
        def about():
            Visit().add_visit('about')
            return render_template('about.html')

        # ---  Login block ---
        @app.route('/login', methods=['POST', 'GET'])
        def login_page():
            Visit().add_visit('login')
            login = request.form.get('login')
            password = request.form.get('password')
            if login and password:
                user = Users.query.filter_by(login=login).first()

                if user and check_password_hash(user.password, password):
                    login_user(user)

                    next_page = request.args.get('next')
                    if next_page:
                        return redirect(next_page)
                    else:
                        return redirect(url_for('main'))
                else:
                    flash('Login or password incorrect')
            else:
                flash('Please fill login and password fields')
            return render_template('users/login.html', user=current_user, title='ItStep Blog: Login', )

        @app.route('/logout', methods=['POST', 'GET'])
        @login_required
        def logout():
            logout_user()
            return redirect(url_for('main'))

        @manager.user_loader
        def load_user(user_id):
            return Users.query.get(user_id)
