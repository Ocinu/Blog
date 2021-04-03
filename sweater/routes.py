from flask import render_template, abort, request, redirect, flash, url_for
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash

from sweater import app
from sweater.articles import Articles, NewUser
from sweater.models import User, db, Category, Likes

item = Articles()
articles = item.update_articles()


@app.before_request
def before_request():
    global articles
    articles = item.update_articles()


@app.route('/', methods=['POST', 'GET'])
def main():
    likes_count = [i.post_id for i in Likes.query.filter_by(user_id=current_user.id).all()]
    user = current_user
    if request.method == 'POST':
        value = request.form['sort_by']
        if value == 'date':
            sorted_articles = item.sort_by_date()
            return render_template('index.html',
                                   title='ItStep Blog',
                                   articles=sorted_articles,
                                   user=user,
                                   likes_count=likes_count)
        else:
            sorted_articles = item.sort_by_author()
            return render_template('index.html',
                                   title='ItStep Blog',
                                   articles=sorted_articles,
                                   user=user,
                                   likes_count=likes_count)
    else:
        posts = item.update_articles()
        return render_template('index.html',
                               title='ItStep Blog',
                               articles=posts,
                               user=user,
                               likes_count=likes_count)


@app.route('/article/<int:post_id>')
def article(post_id):
    for article in articles:
        if article.id == post_id:
            article = item.update_views_count(post_id)
            return render_template('article.html', title='Article', article=article, user=current_user)
    abort(404)


@app.route('/like/<int:post_id>')
@login_required
def add_like(post_id):
    likes_count = [i.post_id for i in Likes.query.filter_by(user_id=current_user.id).all()]
    print(likes_count)
    if post_id not in likes_count:
        item.update_likes_count(post_id, current_user.id)
        return redirect('/')
    abort(404)


@app.route('/new_post', methods=['POST', 'GET'])
@login_required
def new_post():
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
            return render_template('new_post.html', title='New post', user=current_user, categories=categories)
        else:
            current_user.post_number += 1
            db.session.add(current_user)
            db.session.commit()
            return redirect('/')

    else:
        return render_template('new_post.html', title='New post', user=current_user, categories=categories)


@app.route('/edit/<int:post_id>', methods=['POST', 'GET'])
@login_required
def edit_article(post_id):
    article = item.get_article(post_id)
    if request.method == 'POST':
        author = current_user.name
        title = request.form['title']
        text = request.form['text']
        image = request.files['article_image']
        #  валидация полученных данных
        check_errors = item.edit_article(author, title, text, image, post_id)
        if type(check_errors) == str:
            flash(check_errors)
            return render_template('edit.html', title='Edit article', article=article, user=current_user)
        else:
            return redirect('/')
    else:
        return render_template('edit.html', title='Edit article', article=article, user=current_user)


@app.route('/delete/<int:post_id>')
@login_required
def delete_article(post_id):
    for article in articles:
        if article.id == post_id:
            item.delete_article(post_id)
            return render_template('delete.html', article=article, user=current_user)


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


@app.route('/authors')
def authors():
    user = current_user
    all_authors = User.query.all()
    return render_template('authors.html', authors=all_authors, user=user)


@app.after_request
def redirect_to_signin(response):
    if response.status_code == 401:
        return redirect(url_for('login_page') + '?next=' + request.url)

    return response
