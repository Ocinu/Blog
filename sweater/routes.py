from flask import render_template, abort, request, redirect, flash, url_for
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash

from sweater import app
from sweater.models import Articles
from sweater.database import User, db

item = Articles()
articles = item.articles


@app.before_request
def before_request():
    global articles
    articles = item.update_articles()


@app.route('/', methods=['POST', 'GET'])
def main():
    user = current_user
    if request.method == 'POST':
        value = request.form['sort_by']
        if value == 'date':
            articles = item.sort_by_date()
            return render_template('index.html', title='ItStep Blog', articles=articles, user=user)
        else:
            articles = item.sort_by_author()
            return render_template('index.html', title='ItStep Blog', articles=articles, user=user)
    else:
        articles = item.articles
        return render_template('index.html', title='ItStep Blog', articles=articles, user=user)


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
    for article in articles:
        if article.id == post_id:
            item.update_likes_count(post_id)
            return redirect('/')
    abort(404)


@app.route('/new_post', methods=['POST', 'GET'])
@login_required
def new_post():
    if request.method == 'POST':
        author = current_user.name
        title = request.form['title']
        text = request.form['text']
        image = request.files['article_image']

        temp = item.add_new_post(author, title, text, image)
        if type(temp) == str:
            flash(temp)
            return render_template('new_post.html', title='New post', user=current_user)
        else:
            return redirect('/')

    else:
        return render_template('new_post.html', title='New post', user=current_user)


@app.route('/edit/<int:post_id>', methods=['POST', 'GET'])
@login_required
def edit_article(post_id):
    article = item.get_article(post_id)
    if request.method == 'POST':
        author = request.form['author']
        title = request.form['title']
        text = request.form['text']
        try:
            item.edit_article(author, title, text, post_id)
            return redirect('/')
        except Exception as e:
            print(e)
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
    login = request.form.get('login')
    password = request.form.get('password')
    password2 = request.form.get('password2')
    name = request.form.get('name')
    email = request.form.get('email')

    if request.method == 'POST':
        if not (login or password or password2 or name or email):
            flash('Please fill all fields')
        elif password != password2:
            flash('Passwords are not equal')
        else:
            hash_pwd = generate_password_hash(password)
            new_user = User(login=login, password=hash_pwd, name=name, email=email)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login_page'))

    return render_template('register.html', user=current_user)


@app.route('/logout', methods=['POST', 'GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('main'))


@app.after_request
def redirect_to_signin(response):
    if response.status_code == 401:
        return redirect(url_for('login_page') + '?next=' + request.url)

    return response
