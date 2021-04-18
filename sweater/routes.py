from flask import render_template, abort, request, redirect, flash, url_for
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash

from sweater import app
from sweater.articles import Articles, NewUser, Author, NewArticle, Post
from sweater.models import User, Category, Likes, Tag

item = Articles()


def likes_count():
    try:
        likes = [i.post_id for i in Likes.query.filter_by(user_id=current_user.id).all()]
    except:
        likes = []
    return likes


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
    categories = Category.query.all()
    if request.method == 'POST':
        value = request.form['sort_by']
        if value == 'date':
            sorted_articles = item.sort_by_date()
            return render_template('index.html',
                                   title='ItStep Blog',
                                   articles=sorted_articles,
                                   user=current_user,
                                   likes_count=likes_count(),
                                   categories=categories)
        else:
            sorted_articles = item.sort_by_author()
            return render_template('index.html',
                                   title='ItStep Blog',
                                   articles=sorted_articles,
                                   user=current_user,
                                   likes_count=likes_count(),
                                   categories=categories)
    else:
        posts = Articles().articles
        return render_template('index.html',
                               title='ItStep Blog',
                               articles=posts,
                               user=current_user,
                               likes_count=likes_count(),
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
    return render_template('login.html', user=current_user, title='ItStep Blog: Login', )


@app.route('/register', methods=['POST', 'GET'])
def register():
    # если отправляем форму:
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        password2 = request.form.get('password2')
        name = request.form.get('name')
        email = request.form.get('email')
        slug = request.form.get('slug')
        phone = request.form.get('phone')
        avatar = request.files.get('avatar')

        new_user = NewUser(name, email, slug, phone, avatar, login, password, password2)

        # переменная для проверки метода в шаблоне
        check_first_iter = False

        # проверяем все ли поля заполнены
        if not (login or password or password2 or name or email or phone or avatar):
            flash('Please fill all fields')
            return render_template('register.html',
                                   title='ItStep Blog: Registration',
                                   user=current_user,
                                   errors=new_user.errors,
                                   check=check_first_iter,
                                   edit_info=new_user)

        # если есть ошибки выводим их над полями, иначем добавляем юзера и переходим на логин
        if len(new_user.errors) > 0:
            return render_template('register.html',
                                   title='ItStep Blog: Registration',
                                   user=current_user,
                                   errors=new_user.errors,
                                   check=check_first_iter,
                                   edit_info=new_user
                                   )
        new_user.add_new_user(avatar)
        return redirect(url_for('login_page'))
    check_first_iter = True
    return render_template('register.html',
                           title='ItStep Blog: Registration',
                           user=current_user,
                           errors={},
                           check=check_first_iter,
                           edit_info={}
                           )


@app.route('/logout', methods=['POST', 'GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('main'))


# ---  Article block  ---

@app.route('/article/<int:post_id>')
def article(post_id):
    unit = Post(post_id)
    full_info = Post(post_id).post
    unit.update_views_count()
    return render_template('article.html', title='Article: ' + full_info.title, article=full_info, user=current_user)


@app.route('/new_article', methods=['POST', 'GET'])
@login_required
def new_article():
    categories = Category.query.all()
    if request.method == 'POST':
        author_id = current_user.id
        category_id = request.form['category_id']
        title = request.form['title']
        tags = request.form['tags']
        text = request.form['text']
        image = request.files['article_image']

        new_post = NewArticle(author_id, category_id, title, tags, text, image)

        # переменная для проверки метода в шаблоне
        check_first_iter = False

        if len(new_post.errors) > 0:
            return render_template('new_article.html',
                                   title='New post',
                                   user=current_user,
                                   errors=new_post.errors,
                                   check=check_first_iter,
                                   edit_info=new_post,
                                   categories=categories
                                   )
        new_post.add_new_article(image)
        return redirect('/')
    check_first_iter = True
    return render_template('new_article.html',
                           title='New post',
                           user=current_user,
                           errors={},
                           check=check_first_iter,
                           categories=categories)


@app.route('/edit/<int:post_id>', methods=['POST', 'GET'])
@login_required
def edit_article(post_id):
    unit = Post(post_id)
    edit_info = unit.post
    categories = Category.query.all()
    if request.method == 'POST':
        category_id = request.form['category_id']
        title = request.form['title']
        text = request.form['text']
        image = request.files['article_image']

        unit.edit_post(title, text, category_id, image)
        if len(unit.errors) == 0:
            return redirect('/')
        return render_template('edit_post.html',
                               title='Edit article:' + edit_info.title,
                               edit_info=edit_info,
                               user=current_user,
                               errors=unit.errors,
                               categories=categories)

    return render_template('edit_post.html',
                           title='Edit article:' + edit_info.title,
                           edit_info=edit_info,
                           user=current_user,
                           categories=categories)


@app.route('/delete/<int:post_id>')
@login_required
def delete_article(post_id):
    unit = Post(post_id)
    delete_info = unit.post
    unit.delete_post()
    return render_template('delete.html', article=delete_info, user=current_user)


@app.route('/like/<int:post_id>')
@login_required
def add_like(post_id):
    likes = [i.post_id for i in Likes.query.filter_by(user_id=current_user.id).all()]
    unit = Post(post_id)
    if post_id not in likes:
        unit.update_likes_count(post_id, current_user.id)
        return redirect(request.referrer or url_for('main'))
    abort(404)


@app.route('/category/<int:category_id>', methods=['POST', 'GET'])
def category(category_id):
    categories = Category.query.all()
    sort_by_category = Category.query.get(category_id)
    return render_template('index.html',
                           title='ItStep Blog',
                           articles=sort_by_category.articles,
                           user=current_user,
                           likes_count=likes_count(),
                           categories=categories)


@app.route('/tag/<int:tag_id>')
def tag(tag_id):
    categories = Category.query.all()
    sort_by_tag = Tag.query.get(tag_id)
    return render_template('index.html',
                           title='ItStep Blog',
                           articles=sort_by_tag.articles,
                           user=current_user,
                           likes_count=likes_count(),
                           categories=categories)


# ---  Users block  ---

@app.route('/authors')
def authors():
    user = current_user
    all_authors = User.query.all()
    return render_template('authors.html', title='ItStep Blog: Authors', authors=all_authors, user=user)


@app.route('/author/<int:user_id>')
@login_required
def user_info(user_id):
    # исключаем ошибку, если база лайков еще пустая
    try:
        likes = len(Likes.query.filter_by(user_id=user_id).all())
    except:
        likes = 0
    author = User.query.get_or_404(user_id)
    return render_template('author.html',
                           title='ItStep Blog: ' + author.name,
                           user=current_user,
                           likes_count=likes,
                           author=author)


@app.route('/delete_user/<int:user_id>')
@login_required
def delete_user(user_id):
    if user_id == current_user.id:
        user = Author(user_id)
        user.delete_user()
        return redirect(url_for('logout'))
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
            slug = request.form.get('slug')
            email = request.form.get('email')
            phone = request.form.get('phone')
            avatar = request.files.get('avatar')

            if edit_info.check_password(password):
                edit_info.edit_info(login, name, slug, email, phone, avatar)

                if len(edit_info.errors) == 0:
                    return redirect('/authors')

                return render_template('edit_user.html',
                                       title='Edit: ' + edit_info.user.name,
                                       edit_info=edit_info.user,
                                       errors=edit_info.errors,
                                       user=current_user)
            flash('Incorrect password')
            return render_template('edit_user.html',
                                   title='Edit: ' + edit_info.user.name,
                                   edit_info=edit_info.user,
                                   errors={},
                                   user=current_user)
        return render_template('edit_user.html',
                               title='Edit: ' + edit_info.user.name,
                               edit_info=edit_info.user,
                               errors={},
                               user=current_user)
    abort(403)


@app.route('/edit_slug/<int:user_id>', methods=['POST', 'GET'])
@login_required
def edit_slug(user_id):
    if user_id == current_user.id:
        edit_info = Author(user_id)
        if request.method == 'POST':
            slug = request.form.get('slug')
            password = request.form.get('password')
            if edit_info.check_password(password):
                edit_info.edit_slug(slug)
                if len(edit_info.errors) == 0:
                    return redirect('/authors')
                return render_template('edit_slug.html',
                                       title='Edit slug: ' + edit_info.user.name,
                                       edit_info=edit_info.user,
                                       errors=edit_info.errors,
                                       user=current_user)
            flash('Incorrect password')
            return render_template('edit_slug.html',
                                   title='Edit slug: ' + edit_info.user.name,
                                   edit_info=edit_info.user,
                                   errors={},
                                   user=current_user)
        return render_template('edit_slug.html',
                               title='Edit slug: ' + edit_info.user.name,
                               edit_info=edit_info.user,
                               errors={},
                               user=current_user)
    abort(403)


@app.route('/edit_password/<int:user_id>', methods=['POST', 'GET'])
@login_required
def edit_password(user_id):
    if user_id == current_user.id:
        edit_info = Author(user_id)
        if request.method == 'POST':
            password = request.form.get('password')
            new_password = request.form.get('new_password')
            new_password2 = request.form.get('new_password2')
            if edit_info.check_password(password):
                edit_info.edit_password(new_password, new_password2)
                if len(edit_info.errors) == 0:
                    return redirect('/authors')
                return render_template('edit_password.html',
                                       title='Edit password: ' + edit_info.user.name,
                                       edit_info=edit_info.user,
                                       errors=edit_info.errors,
                                       user=current_user)
            flash('Incorrect password')
            return render_template('edit_password.html',
                                   title='Edit password: ' + edit_info.user.name,
                                   edit_info=edit_info.user,
                                   errors={},
                                   user=current_user)
        return render_template('edit_password.html',
                               title='Edit password: ' + edit_info.user.name,
                               edit_info=edit_info.user,
                               errors={},
                               user=current_user)
    abort(403)
