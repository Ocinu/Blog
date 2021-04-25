from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_login import LoginManager

from config import secret_key, UPLOAD_FOLDER
import logging.config

logging.config.fileConfig('logger.conf')
logger = logging.getLogger('main')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = secret_key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
manager = LoginManager(app)
