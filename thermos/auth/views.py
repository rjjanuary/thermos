import json

from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user
from time import sleep

from . import auth
from .. import db, stats_client
from ..models import User
from .forms import LoginForm, SignupForm

@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        #login and validate user
        user = User.get_by_username(username=form.username.data)
        if user is not None and user.check_password(form.password.data):
            stats_client.incr('thermos.logins.success')             # added line to increment success counter
            login_user(user, form.remember_me.data)
            flash('logged in successfully as {}.'.format(user.username))
            return redirect(request.args.get('next') or url_for('main.index'))
            #^'next' will redirect the user to where they were attempting to go.  (look at browser query string)
        flash('Incorrect username or password.')
        stats_client.incr('thermos.logins.fail')                    # added line to increment fail counter
        sleep(2)                                                    # added sleep to invalid login attempt
    return render_template('login.html', form=form)

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@auth.route('/signup', methods=['GET','POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Welcome, {}! Please login to continue.'.format(user.username))
        return redirect(url_for('.login'))
    return render_template('signup.html', form=form)