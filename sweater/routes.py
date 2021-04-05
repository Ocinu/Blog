import os

from flask import render_template, abort, request, redirect, flash, url_for
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy.orm import Session
from werkzeug.security import check_password_hash

from sweater import app
from sweater.articles import Articles, NewUser, Author
from sweater.models import User, db, Category, Likes

item = Articles()
articles = item.update_articles()

session = Session()


@app.before_request
def before_request():
    global articles
    articles = item.update_articles()


@app.after_request
def redirect_to_signin(response):
    if response.status_code == 401:
        return redirect(url_for('login_page') + '?next=' + request.url)
    return response


@app.route('/', methods=['POST', 'GET'])
def main():
    categories = Category.query.all()
    try:
        likes_count = [i.post_id for i in Likes.query.filter_by(user_id=current_user.id).all()]
    except:
        likes_count = []
    if request.method == 'POST':
        value = request.form['sort_by']
        if value == 'date':
            sorted_articles = item.sort_by_date()
            return render_template('index.html',
                                   title='ItStep Blog',
                                   articles=sorted_articles,
                                   user=current_user,
                                   likes_count=likes_count,
                                   categories=categories)
        else:
            sorted_articles = item.sort_by_author()
            return render_template('index.html',
                                   title='ItStep Blog',
                                   articles=sorted_articles,
                                   user=current_user,
                                   likes_count=likes_count,
                                   categories=categories)
    else:
        posts = item.update_articles()
        return render_template('index.html',
                               title='ItStep Blog',
                               articles=posts,
                               user=current_user,
                               likes_count=likes_count,
                               categories=categories)


# ---  Login block ---

@app.route('/login', methods=['POST', 'GET'])
def login_page():
    login = request.form.get('login')
    password = request.form.get('password')
    if login and password:
        user = User.query.filter_by(login=login).first()

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
    return render_template('login.html', user=current_user)


@app.route('/register', methods=['POST', 'GET'])
def register():
    # если отправляем форму:
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        password2 = request.form.get('password2')
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        avatar = request.files.get('avatar')

        # проверяем все ли поля заполнены
        if not (login or password or password2 or name or email or phone or avatar):
            flash('Please fill all fields')
            return render_template('register.html', user=current_user)

        new_user = NewUser(name, email, phone, avatar, login, password, password2)

        # если есть ошибки выводим флэш, иначем добавляем юзера и переходим на логин
        check_errors = new_user.add_new_user(avatar)
        if type(check_errors) == str:
            flash(check_errors)
            return render_template('register.html', user=current_user)
        return redirect(url_for('login_page'))

    return render_template('register.html', user=current_user)


@app.route('/logout', methods=['POST', 'GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('main'))


# ---  Article block  ---

@app.route('/article/<int:post_id>')
def article(post_id):
    for full_info in articles:
        if full_info.id == post_id:
            full_info = item.update_views_count(post_id)
            return render_template('article.html', title='Article', article=full_info, user=current_user)
    abort(404)


@app.route('/new_article', methods=['POST', 'GET'])
@login_required
def new_article():
    categories = Category.query.all()
    if request.method == 'POST':
        author_id = current_user.id
        category_id = request.form['category_id']
        title = request.form['title']
        text = request.form['text']
        image = request.files['article_image']

        check_errors = item.add_new_post(author_id, title, text, image, category_id)
        if type(check_errors) == str:
            flash(check_errors)
            return render_template('new_article.html', title='New post', user=current_user, categories=categories)
        else:
            current_user.post_number += 1
            db.session.add(current_user)
            db.session.commit()
            return redirect('/')

    else:
        return render_template('new_article.html', title='New post', user=current_user, categories=categories)


@app.route('/edit/<int:post_id>', methods=['POST', 'GET'])
@login_required
def edit_article(post_id):
    edit_info = item.get_article(post_id)
    if request.method == 'POST':
        author = current_user.name
        title = request.form['title']
        text = request.form['text']
        image = request.files['article_image']
        #  валидация полученных данных
        check_errors = item.edit_article(author, title, text, image, post_id)
        if type(check_errors) == str:
            flash(check_errors)
            return render_template('edit.html', title='Edit article', article=edit_info, user=current_user)
        else:
            return redirect('/')
    else:
        return render_template('edit.html', title='Edit article', article=edit_info, user=current_user)


@app.route('/delete/<int:post_id>')
@login_required
def delete_article(post_id):
    for delete_info in articles:
        if delete_info.id == post_id:
            item.delete_article(post_id)
            return render_template('delete.html', article=delete_info, user=current_user)


@app.route('/like/<int:post_id>')
@login_required
def add_like(post_id):
    likes_count = [i.post_id for i in Likes.query.filter_by(user_id=current_user.id).all()]
    if post_id not in likes_count:
        item.update_likes_count(post_id, current_user.id)
        return redirect('/')
    abort(404)


# ---  Users block  ---

@app.route('/authors')
def authors():
    user = current_user
    all_authors = User.query.all()
    return render_template('authors.html', authors=all_authors, user=user)


@app.route('/author/<int:user_id>')
@login_required
def user_info(user_id):
    # исключаем ошибку, если база лайков еще пустая
    try:
        likes_count = len(Likes.query.filter_by(user_id=user_id).all())
    except:
        likes_count = 0
    author = User.query.get_or_404(user_id)
    return render_template('author.html',
                           user=current_user,
                           likes_count=likes_count,
                           author=author)


@app.route('/delete_user/<int:user_id>')
@login_required
def delete_user(user_id):
    # проверка на подмену id в строке запроса
    if user_id == current_user.id:
        user = User.query.get_or_404(user_id)
        # удаление аватарки
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], user.avatar))
        # удаление всех постов автора
        for post in user.articles:
            item.delete_article(post.id)
        db.session.delete(user)
        db.session.commit()
        return redirect('/authors')
    abort(403)


@app.route('/edit_user/<int:user_id>', methods=['POST', 'GET'])
@login_required
def edit_user(user_id):
    if user_id == current_user.id:
        edit_info = Author(user_id)
        if request.method == 'POST':
            login = request.form.get('login')
            password = request.form.get('password')
            name = request.form.get('name')
            email = request.form.get('email')
            phone = request.form.get('phone')

            if edit_info.check_password(password):
                edit_info.edit_info(login, name, email, phone)

                if len(edit_info.errors) == 0:
                    edit_info.save_db()
                    return redirect('/authors')

                flash(edit_info.errors)
                return render_template('edit_user.html', edit_info=edit_info.user, user=current_user)
            flash('Incorrect password')
            return render_template('edit_user.html', edit_info=edit_info.user, user=current_user)
        return render_template('edit_user.html', edit_info=edit_info.user, user=current_user)
    abort(403)
