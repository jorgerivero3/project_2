from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import os
from flask_mail import Mail

application = Flask(__name__)
application.config['SECRET_KEY'] = 'c435bd07880364149cdf9661f1994db4'
application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'


db = SQLAlchemy(application)
bcrypt = Bcrypt(application)

login_manager = LoginManager(application)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'


application.config['MAIL_SERVER'] = 'smtp.googlemail.com'
application.config['MAIL_PORT'] = 587
application.config['MAIL_USE_TLS'] = True
application.config['MAIL_USERNAME'] = 'cs329efall18project0'
application.config['MAIL_PASSWORD'] = 'texascompsci18'
mail = Mail(application)


from Application import routes