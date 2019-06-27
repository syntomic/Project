# -*- coding: utf-8 -*-

from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_moment import Moment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_debugtoolbar import DebugToolbarExtension
from flask_sslify import SSLify

bootstrap = Bootstrap()
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
moment = Moment()
toolbar = DebugToolbarExtension()
migarte = Migrate()
#sslify = SSLify()


@login_manager.user_loader
def load_user(user_id):
    from myblog.models import Admin
    user = Admin.query.get(int(user_id))
    return user

login_manager.login_view = 'auth.login'

login_manager.login_message_category = 'warning'