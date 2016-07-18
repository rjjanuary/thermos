import os

from flask import Flask #, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_moment import Moment
from flask_debugtoolbar import DebugToolbarExtension

from .config import config_by_name

db = SQLAlchemy()

#Configure Authentication
login_manager=LoginManager()
login_manager.session_protection = "strong"
login_manager.login_view = "auth.login"              #set where to send people needing to log in

#enable debugtoolbar
toolbar = DebugToolbarExtension()

#for displaying timestamps
moment = Moment()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    db.init_app(app)
    login_manager.init_app(app)
    moment.init_app(app)
    toolbar.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint, url_prefix='/')

    from .bookmarks import bookmarks as bkm_blueprint
    app.register_blueprint(bkm_blueprint, url_prefix='/bookmarks')

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    return app

#
# basedir = os.path.abspath(os.path.dirname(__file__))
#
#     app = Flask(__name__)
#     app.config['SECRET_KEY'] = '\xf7]\x88\x89\x8a\xd8\x99\x0cf\x91\xc9c\x9f\n\x03\x9f8\xadA\xd2\xfc\xf5\x17\x0e'
#     app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'thermos.db')
#     app.config['DEBUG'] = True
#     db = SQLAlchemy(app)
#
#                   #integrates login into our flask app
#
# toolbar = DebugToolbarExtension(app)
#
# # app.logger.setLevel(DEBUG)
# # app.logger.debug('__init__ finished')
#
# from .auth import auth as auth_blueprint
# app.register_blueprint(auth_blueprint, url_prefix='/auth')
#
# import views
# import models