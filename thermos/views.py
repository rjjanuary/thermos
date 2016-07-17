from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import login_required, login_user, logout_user, current_user

from models import Bookmark, User
from forms import BookmarkForm, LoginForm, SignupForm
from thermos import db, app, login_manager


@login_manager.user_loader
#^tells flask-login how to retrieve a user by id
def load_user(userid):
    return User.query.get(int(userid))

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', new_bookmarks=Bookmark.newest(5))


@app.route('/add', methods=['GET','POST'])
@login_required
def add():
    form = BookmarkForm()
    if form.validate_on_submit():
        url = form.url.data
        description = form.description.data
        bm = Bookmark(user=current_user,url=url, description=description)
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

@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        #login and validate user
        user = User.get_by_username(username=form.username.data)
        if user is not None and user.check_password(form.password.data):
            login_user(user, form.remember_me.data)
            flash('logged in successfully as {}.'.format(user.username))
            return redirect(request.args.get('next') or url_for('index'))
            #^'next' will redirect the user to where they were attempting to go.  (look at browser query string)
        flash('Incorrect username or password.')
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/signup', methods=['GET','POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Welcome, {}! Please login to continue.'.format(user.username))
        return redirect(url_for('login'))
    return render_template('signup.html', form=form)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"),404


@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"),500
