from flask import render_template, redirect, abort, url_for, request, flash
from flask_login import login_required, current_user

from application.units.articles.controller import LikesController, PostController
from application.units.users.controller import UserController, UsersTotal, NewUser


class UserRoutes:
    def __init__(self, app):
        self.app = app
        self.likes = LikesController()
        self.params = {
            'user': current_user,
            'errors': {},
            'edit_info': {}
        }

        @app.route('/authors')
        def authors():
            self.params['title'] = 'ItStep Blog: Authors'
            self.params['authors'] = UsersTotal().users
            return render_template('users/authors.html', **self.params)

        @app.route('/author/<int:user_id>')
        @login_required
        def user_info(user_id):
            user = UserController(user_id).user
            self.params['likes_number'] = LikesController().likes_number(user_id)
            self.params['author'] = user
            self.params['title'] = 'ItStep Blog: ' + user.name
            return render_template('users/author.html', **self.params)

        @app.route('/register', methods=['POST', 'GET'])
        def register():
            self.params['check'] = True
            self.params['title'] = 'ItStep Blog: Registration'

            if request.method == 'POST':
                new_user = NewUser(**request.files, **request.form)
                self.params['check'] = False

                # если есть ошибки выводим их над полями, иначем добавляем юзера и переходим на логин
                if len(new_user.errors) > 0:
                    self.params['errors'] = new_user.errors
                    self.params['edit_info'] = new_user
                    return render_template('users/register.html', **self.params)
                new_user.add_new_user(**request.files)
                return redirect(url_for('login_page'))
            return render_template('users/register.html', **self.params)

        @app.route('/delete_user/<int:user_id>')
        @login_required
        def delete_user(user_id):
            if user_id == current_user.id or current_user.access_rights > 4:
                delete_info = UserController(user_id)
                for post in delete_info.user.articles:
                    PostController(post.id).delete_post()
                delete_info.delete_user()
                return redirect(url_for('logout'))
            abort(403)

        @app.route('/edit_user/<int:user_id>', methods=['POST', 'GET'])
        @login_required
        def edit_user(user_id):
            if user_id == current_user.id:
                edit_info = UserController(user_id)
                self.params['title'] = 'Edit: ' + edit_info.user.name
                self.params['edit_info'] = edit_info.user

                if request.method == 'POST':
                    if edit_info.check_password(request.form.get('password')):
                        edit_info.edit_info(**request.files, **request.form)
                        self.params['edit_info'] = edit_info.user
                        self.params['errors'] = edit_info.errors

                        if len(edit_info.errors) == 0:
                            return redirect('/authors')
                        return render_template('users/edit_user.html', **self.params)
                    flash('Incorrect password')
                    return render_template('users/edit_user.html', **self.params)
                return render_template('users/edit_user.html', **self.params)
            abort(403)

        @app.route('/edit_slug/<int:user_id>', methods=['POST', 'GET'])
        @login_required
        def edit_slug(user_id):
            if user_id == current_user.id:
                edit_info = UserController(user_id)
                self.params['title'] = 'Edit slug: ' + edit_info.user.name
                self.params['edit_info'] = edit_info.user

                if request.method == 'POST':
                    slug = request.form.get('slug')
                    password = request.form.get('password')

                    if edit_info.check_password(password):
                        edit_info.edit_slug(slug)
                        self.params['errors'] = edit_info.errors

                        if len(edit_info.errors) == 0:
                            return redirect('/authors')
                        return render_template('users/edit_slug.html', **self.params)
                    flash('Incorrect password')
                    return render_template('users/edit_slug.html', **self.params)
                return render_template('users/edit_slug.html', **self.params)
            abort(403)

        @app.route('/edit_password/<int:user_id>', methods=['POST', 'GET'])
        @login_required
        def edit_password(user_id):
            if user_id == current_user.id:
                edit_info = UserController(user_id)
                self.params['title'] = 'Edit password: ' + edit_info.user.name
                self.params['edit_info'] = edit_info.user

                if request.method == 'POST':
                    password = request.form.get('password')
                    new_password = request.form.get('new_password')
                    new_password2 = request.form.get('new_password2')

                    if edit_info.check_password(password):
                        edit_info.edit_password(new_password, new_password2)
                        self.params['errors'] = edit_info.errors

                        if len(edit_info.errors) == 0:
                            return redirect('/authors')
                        return render_template('users/edit_password.html', **self.params)
                    flash('Incorrect password')
                    return render_template('users/edit_password.html', **self.params)
                return render_template('users/edit_password.html', **self.params)
            abort(403)

        @app.route('/set_access/<int:user_id>', methods=['POST'])
        def set_access(user_id):
            if current_user.access_rights > 4:
                UserController(user_id).set_access(**request.form)
                return redirect(url_for('admin'))
            abort(403)
