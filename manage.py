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
def import_bookmarks(user_seed=0, max_bookmarks=2000, total_record_count=1000):

    class fakeuser_factory(object):
        def __init__(self,user_seed=user_seed):
            self._user_count=int(user_seed)
        def usernumber(self):
            self._user_count += 1
            return self._user_count
        def create_user(self):
            username = 'user{}'.format(self.usernumber())
            db.session.add(User(username=username, email="{}@example.com".format(username), password=username))
            return User.get_by_username(username)

    uf = fakeuser_factory()

    user_record_count = int(max_bookmarks)*10                                   #seed first user problems
    total_record_count = int(total_record_count)
    max_bookmarks=int(max_bookmarks)

    ins_user = uf.create_user()
    with open('./thermos/data/majestic_1000.csv') as f:
        next(f)
        for l in f:
            print 't:{} u:{}'.format(total_record_count,user_record_count)
            total_record_count -= 1
            if total_record_count <= 0:
                print 'Hit maximum import limit of {}'.format(total_record_count)
                break                     #bail if we've hit our max record count
            if user_record_count <= 0:
                db.session.commit()
                user_record_count = random.randrange(1, max_bookmarks)
                ins_user = uf.create_user()
                print 'created user:{} max bookmarks:{}'.format(ins_user.username,user_record_count)
            rank,rank2,url = l.split(',')
            db.session.add(Bookmark(url=url.strip(), description=url.strip(), user=ins_user, tags='imported'))
            # print 'inserted bookmark:{}'.format(url.strip())
            user_record_count -= 1
    db.session.commit()

@manager.command
def dropdb():
    if prompt_bool(
        "Are you sure you want to lose all your data"):
        db.drop_all()
        print 'Dropped the database'

if __name__ == '__main__':
    manager.run()

