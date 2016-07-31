from flask import render_template

from . import main
from .. import login_manager
from ..models import User, Bookmark, Tag
#from flask_statsd import statsd_client

@login_manager.user_loader
#^tells flask-login how to retrieve a user by id
def load_user(userid):
    return User.query.get(int(userid))

@main.route('/')
# @main.route('/index')
def index():
    # with statsd_client.timer('index'):
        return render_template('index.html', new_bookmarks=Bookmark.newest(5))


@main.app_errorhandler(403)
def page_not_found(e):
    return render_template("403.html"),403


@main.app_errorhandler(404)
def page_not_found(e):
    return render_template("404.html"),404


@main.app_errorhandler(500)
def server_error(e):
    return render_template("500.html"),500


@main.app_context_processor
def inject_tags():
    return dict(all_tags=Tag.all)