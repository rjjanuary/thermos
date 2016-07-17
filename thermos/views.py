from flask import Flask, render_template, request, redirect, url_for, flash
from models import Bookmark, User
from forms import BookmarkForm
from thermos import db, app

# fake login
def logged_in_user():
    return User.query.filter_by(username='rjanuary').first()

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', new_bookmarks=Bookmark.newest(5))


@app.route('/add', methods=['GET','POST'])
def add():
    form = BookmarkForm()
    if form.validate_on_submit():
        url = form.url.data
        description = form.description.data
        bm = Bookmark(user=logged_in_user(),url=url, description=description)
        db.session.add(bm)
        db.session.commit()
        # app.logger.debug("Stored Bookmark: '{}'".format(url))
        flash("Stored Bookmark: '{}'".format(url))
        return redirect(url_for('index'))
    return render_template('add.html',form=form)

@app.route('/user/<username>')
def user(username):
    user= User.query.filter_by(username=username).first_or_404()
    return render_template('user.html',user=user)

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"),404

@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"),500
