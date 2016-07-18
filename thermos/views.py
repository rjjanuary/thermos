from flask import Flask, render_template, request, redirect, url_for, flash, abort
#from flask_login import login_required, current_user

from models import Bookmark, User, Tag
from thermos import db, app, login_manager





# @app.route('/login', methods=['GET','POST'])
# def login():
#     form = LoginForm()
#     if form.validate_on_submit():
#         #login and validate user
#         user = User.get_by_username(username=form.username.data)
#         if user is not None and user.check_password(form.password.data):
#             login_user(user, form.remember_me.data)
#             flash('logged in successfully as {}.'.format(user.username))
#             return redirect(request.args.get('next') or url_for('index'))
#             #^'next' will redirect the user to where they were attempting to go.  (look at browser query string)
#         flash('Incorrect username or password.')
#     return render_template('login.html', form=form)


# @app.route('/logout')
# def logout():
#     logout_user()
#     return redirect(url_for('index'))
#
#
# @app.route('/signup', methods=['GET','POST'])
# def signup():
#     form = SignupForm()
#     if form.validate_on_submit():
#         user = User(email=form.email.data,
#                     username=form.username.data,
#                     password=form.password.data)
#         db.session.add(user)
#         db.session.commit()
#         flash('Welcome, {}! Please login to continue.'.format(user.username))
#         return redirect(url_for('login'))
#     return render_template('signup.html', form=form)
#



