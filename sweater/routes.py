from flask import render_template, abort, request, redirect

from sweater import app
from sweater.models import Articles

item = Articles()
articles = item.articles


@app.before_request
def before_request():
    global articles
    articles = item.update_articles()


@app.route('/', methods=['POST', 'GET'])
def main():
    if request.method == 'POST':
        value = request.form['sort_by']
        if value == 'date':
            articles = item.sort_by_date()
            return render_template('index.html', title='ItStep Blog', articles=articles)
        else:
            articles = item.sort_by_author()
            return render_template('index.html', title='ItStep Blog', articles=articles)
    else:
        articles = item.articles
        return render_template('index.html', title='ItStep Blog', articles=articles)


@app.route('/article/<int:post_id>')
def article(post_id):
    for article in articles:
        if article.id == post_id:
            article = item.update_views_count(post_id)
            return render_template('article.html', title='Article', article=article)
    abort(404)


@app.route('/like/<int:post_id>')
def add_like(post_id):
    for article in articles:
        if article.id == post_id:
            item.update_likes_count(post_id)
            return redirect('/')
    abort(404)


@app.route('/new_post', methods=['POST', 'GET'])
def new_post():
    if request.method == 'POST':
        author = request.form['author']
        title = request.form['title']
        text = request.form['text']

        try:
            item.add_new_post(author, title, text)
            return redirect('/')
        except Exception as e:
            print(e)
    else:
        return render_template('new_post.html', title='New post')


@app.route('/edit/<int:post_id>', methods=['POST', 'GET'])
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
        return render_template('edit.html', title='Edit article', article=article)


@app.route('/delete/<int:post_id>')
def delete_article(post_id):
    for article in articles:
        if article.id == post_id:
            item.delete_article(post_id)
            return render_template('delete.html', article=article)
