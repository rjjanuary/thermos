import os

from flask import Flask #, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_moment import Moment
from flask_debugtoolbar import DebugToolbarExtension

from logging import DEBUG


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = '\xf7]\x88\x89\x8a\xd8\x99\x0cf\x91\xc9c\x9f\n\x03\x9f8\xadA\xd2\xfc\xf5\x17\x0e'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'thermos.db')
app.config['DEBUG'] = True
db = SQLAlchemy(app)

#Configure Authentication
login_manager=LoginManager()
login_manager.session_protection = "strong"
login_manager.login_view = "auth.login"              #set where to send people needing to log in
login_manager.init_app(app)                     #integrates login into our flask app

#enable debugtoolbar
toolbar = DebugToolbarExtension(app)

#for displaying timestamps
moment = Moment(app)
# app.logger.setLevel(DEBUG)
# app.logger.debug('__init__ finished')

from .auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint, url_prefix='/auth')

import views
import models