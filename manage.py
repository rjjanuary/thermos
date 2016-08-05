import os
from thermos import create_app, db
from flask_script import Manager, prompt_bool
from flask_migrate import Migrate, MigrateCommand

###load models to make flask migrate aware of them
from thermos.models import User, Bookmark, Tag, tags
##########################

import random, pymysql
from datetime import datetime

app = create_app(os.getenv('THERMOS_ENV') or 'dev')
print ('THERMOS_ENV {} '.format(os.getenv('THERMOS_ENV')))

manager = Manager(app)

migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)

@manager.command
def insert_data():
    # db.create_all()
    def add_bookmark(user, url, description, tags):
        print 'adding bookmark user:{} url:{} desc:{} tags:{}'.format(user, url, description, tags)
        db.session.add(Bookmark(url=url, description=description, user=user, tags=tags))

    db.session.add(User(username="rjanuary", email="rjanuary@example.com", password="test"))
    db.session.add(User(username="other", email="other@example.com", password="test"))

    ins_user = User.get_by_username("rjanuary")

    add_bookmark(ins_user,'http://www.google.com','Google - Search Engine','search, all the stuff, yea!')
    add_bookmark(ins_user,'http://www.python.org','Primary Python site','programming,knowledge')

    db.session.commit()
    print 'Initialized the database'

@manager.command
def import_bookmarks():
    def gen_username():
        user_count =+ 1
        return 'imp_{}'.format(user_count)

    user_count = 0
    record_count = 0
    max_record_count = 1000
    conn = pymysql.connect(host='10.162.2.55', port=3306, user='thermos', passwd='thermos', db='thermos')
    cur = conn.cursor()

    username = gen_username()
    db.session.add(User(username=username, email="{}@example.com".format(username), password=username))
    ins_user = User.get_by_username(username)

    with open('./thermos/data/majestic_test.csv') as f:
        next(f)
        for l in f:
            rank,rank2,url = l.split(',')
            db.session.add(Bookmark(url=url.strip(), description=url.strip(), user=ins_user, tags='imported'))
            record_count += 1
            if record_count > max_record_count:
                conn.commit()
    conn.commit()

    db.session.add(User(username="user", email="{}@example.com".format(user), password=user))


@manager.command
def dropdb():
    if prompt_bool(
        "Are you sure you want to lose all your data"):
        db.drop_all()
        print 'Dropped the database'

if __name__ == '__main__':
    manager.run()

