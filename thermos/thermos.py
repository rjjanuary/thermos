from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from logging import DEBUG

app = Flask(__name__)
app.logger.setLevel(DEBUG)

bookmarks=[]
app.config['SECRET_KEY'] = '\xf7]\x88\x89\x8a\xd8\x99\x0cf\x91\xc9c\x9f\n\x03\x9f8\xadA\xd2\xfc\xf5\x17\x0e'

def store_bookmark(url):
    bookmarks.append(dict(
        url = url,
        user = "rjanuary",
        date = datetime.utcnow()
    ))
class User:
    def __init__(self,firstname,lastname):
        self.firstname=firstname
        self.lastname=lastname
    def initials(self):
        return '{}. {}.'.format(self.firstname[0],self.lastname[0])
    def __str__(self):
        return '{} {}'.format(self.firstname,self.lastname)


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='hey', text=['this','thing'], user=User('ryan','january'))


@app.route('/add', methods=['GET','POST'])
def add():
    if request.method == "POST":
        url = request.form['url']
        store_bookmark(url)
        # app.logger.debug("Stored Bookmark: '{}'".format(url))
        flash("Stored Bookmark: '{}'".format(url))
        return redirect(url_for('index'))
    return render_template('add.html')


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"),404

@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"),500


if __name__ == '__main__':
    app.run(debug=True)