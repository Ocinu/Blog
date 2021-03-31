from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_login import LoginManager

UPLOAD_FOLDER = 'sweater/static/images/'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'some very secret key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
manager = LoginManager(app)

from sweater import models, routes, database
