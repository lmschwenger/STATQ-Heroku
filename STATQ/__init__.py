from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from STATQ.config import Config
import boto3
import os
from datetime import timedelta
s3 = boto3.client('s3', aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID'), aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'))

db = SQLAlchemy()
bcrypt = Bcrypt()

login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
login_manager.login_message = u'Du skal være logget ind for at benytte denne funktion'
login_manager.refresh_view = 'relogin'
login_manager.needs_refresh_message = (u"Session timedout, please re-login")

mail = Mail()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    from STATQ.users.routes import users
    from STATQ.main.routes import main
    from STATQ.errors.handlers import errors
    from STATQ.program.routes import program
    app.register_blueprint(users)
    app.register_blueprint(main)
    app.register_blueprint(errors)
    app.register_blueprint(program)
    @app.before_request
    def before_request():
        session.permanent = True
        app.permanent_session_lifetime = timedelta(seconds=30)
    return app