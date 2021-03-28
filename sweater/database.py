from sweater import db


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String, nullable=False)
    title = db.Column(db.String, nullable=False)
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.Text, default='')
    likes = db.Column(db.Integer, default=0)
    views = db.Column(db.Integer, default=0)