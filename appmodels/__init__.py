from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
#from datetime import timedelta
import os
import pymysql
pymysql.install_as_MySQLdb()

app = Flask(__name__)
app.config['SECRET_KEY'] = '6789d25fd941dab2cfcd9e6c02de038d'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://TutorH_dev:TutorH_dev_pwd@localhost/TutorH_dev_db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'users.signin'
login_manager.login_message_category = 'info'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
#app.config['REMEMBER_COOKIE_DURATION'] = timedelta(seconds = 5)
#app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER')
#app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS')
mail = Mail(app)

from appmodels.users.routes import users
from appmodels.main.routes import main

app.register_blueprint(users)
app.register_blueprint(main)
