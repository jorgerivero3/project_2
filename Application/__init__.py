from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
import os

# creates web "app"
application = Flask(__name__)
application.config['SECRET_KEY'] = 'c435bd07880364149cdf9661f1994db4'
application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

# launches db and encryption
db = SQLAlchemy(application)
bcrypt = Bcrypt(application)

# creates login manager
login_manager = LoginManager(application)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# configuration for email reset
application.config['MAIL_SERVER'] = 'smtp.googlemail.com'
application.config['MAIL_PORT'] = 587
application.config['MAIL_USE_TLS'] = True
application.config['MAIL_USERNAME'] = 'cs329efall18project0'
application.config['MAIL_PASSWORD'] = 'texascompsci18'
mail = Mail(application)

# import at the end to avoid circular imports
from Application import routes