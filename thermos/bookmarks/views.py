# imports for web framework
from flask import render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, login_user, logout_user, current_user

#imports from other parts of the application
from . import bookmarks
from .forms import BookmarkForm
from .. import db
from .. import stats_client
from ..models import User, Bookmark, Tag, Bookmark_flag

#add bookmark
@bookmarks.route('/add', methods=['GET','POST'])
@login_required
def add():
    form = BookmarkForm()
    if form.validate_on_submit():
        url = form.url.data
        description = form.description.data
        tags = form.tags.data
        bm = Bookmark(user=current_user, url=url, description=description, tags=tags)
        db.session.add(bm)
        db.session.commit()
        # app.logger.debug("Stored Bookmark: '{}'".format(url))
        flash("Stored Bookmark: '{}'".format(url))
        stats_client.incr('thermos.bookmarks,operation=add')
        return redirect(url_for('main.index'))

    return render_template('bookmark_form.html',form=form, title="Add a bookmark")

#edit bookmark
@bookmarks.route('/edit/<int:bookmark_id>', methods=['GET','POST'])
@login_required
def edit_bookmark(bookmark_id):
    bookmark = Bookmark.query.get_or_404(bookmark_id)
    if current_user != bookmark.user:
        abort(403)
    form = BookmarkForm(obj=bookmark) #data submitted on user request takes precident over data from database
    if form.validate_on_submit():
        form.populate_obj(bookmark)
        db.session.commit()
        flash("Stored '{}'".format(bookmark.description))
        stats_client.incr('thermos.bookmarks,operation=edit')
        return redirect(url_for('.user',username=current_user.username))
    return render_template('bookmark_form.html', form=form, title="Edit bookmark")

#delete bookmark
@bookmarks.route('/delete/<int:bookmark_id>', methods=['GET','POST'])
@login_required
def delete_bookmark(bookmark_id):
    bookmark = Bookmark.query.get_or_404(bookmark_id)
    if current_user != bookmark.user:
        abort(403)
    if request.method == "POST":
        db.session.delete(bookmark)
        db.session.commit()
        flash("Deleted '{}'".format(bookmark.description))
        stats_client.incr('thermos.bookmarks,operation=delete')
        return redirect(url_for('.user', username=current_user.username))
    else:
        flash("Please confirm deleting the bookmark.")
    return render_template('confirm_delete.html', bookmark=bookmark, nolinks=True)

#display a users bookmarks
@bookmarks.route('/user/<username>')
def user(username):
    user= User.query.filter_by(username=username).first_or_404()
    return render_template('user.html',user=user)

#display list of bookmarks with a tag
@bookmarks.route('/tag/<name>')
def tag(name):
    tag = Tag.query.filter_by(name=name).first_or_404()
    return render_template('tag.html', tag=tag)

@bookmarks.route('/bookmark_flag', methods=['GET'])
def primes():
    count = request.args.get('count')
    print type(count)
    if not count:
        count = 1
    return render_template('primes.html', nbr=Bookmark_flag.find_next(int(count)))