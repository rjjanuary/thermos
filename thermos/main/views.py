from flask import render_template, request
from . import main
from .. import login_manager
from ..models import User, Bookmark, Tag, Bookmark_flag


@login_manager.user_loader
#^tells flask-login how to retrieve a user by id
def load_user(userid):
    return User.query.get(int(userid))

#main page
@main.route('/')
# @main.route('/index')
def index():
    # with statsd_client.timer('index'):
        return render_template('index.html', new_bookmarks=Bookmark.newest(5))

# unauthorized page
@main.app_errorhandler(403)
def page_not_found(e):
    return render_template("403.html"),403

# page not found
@main.app_errorhandler(404)
def page_not_found(e):
    return render_template("404.html"),404

# server error
@main.app_errorhandler(500)
def server_error(e):
    return render_template("500.html"),500

# get list of all tags
@main.app_context_processor
def inject_tags():
    return dict(all_tags=Tag.all)