import os

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = '\xf7]\x88\x89\x8a\xd8\x99\x0cf\x91\xc9c\x9f\n\x03\x9f8\xadA\xd2\xfc\xf5\x17\x0e'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'thermos.db')
app.config['DEBUG'] = True
db = SQLAlchemy(app)

import models
import views

from forms import BookmarkForm
# from models import Bookmark
import models

# class User:
#     def __init__(self,firstname,lastname):
#         self.firstname=firstname
#         self.lastname=lastname
#     def initials(self):
#         return '{}. {}.'.format(self.firstname[0],self.lastname[0])
#     def __str__(self):
#         return '{} {}'.format(self.firstname,self.lastname)
#
# fake login
def logged_in_user():
    return models.User.query.filter_by(username='rjanuary').first()

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', new_bookmarks=models.Bookmark.newest(5))


@app.route('/add', methods=['GET','POST'])
def add():
    form = BookmarkForm()
    if form.validate_on_submit():
        url = form.url.data
        description = form.description.data
        bm = models.Bookmark(user=logged_in_user(),url=url, description=description)
        db.session.add(bm)
        db.session.commit()
        # app.logger.debug("Stored Bookmark: '{}'".format(url))
        flash("Stored Bookmark: '{}'".format(url))
        return redirect(url_for('index'))
    return render_template('add.html',form=form)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"),404

@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"),500


# if __name__ == '__main__':
#     app.run(debug=True)