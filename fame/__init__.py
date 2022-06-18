import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
#from secret_config import email,password

app = Flask(__name__)
app.config['SECRET_KEY'] = '5a0f0691a56dd4d43e1c3f8f32ec17a5'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
#app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
#app.config['MAIL_PORT'] = 587
#app.config['MAIL_USE_TLS'] = True
#app.config['MAIL_USERNAME'] = email
#os.environ.get('EMAIL_USER')
#app.config['MAIL_PASSWORD'] = password
#os.environ.get('EMAIL_PASS')
#mail = Mail(app)


from fame import routes
