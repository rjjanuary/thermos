'''
http://influxdb-python.readthedocs.io/en/latest/examples.html
'''


import os
from thermos import create_app, db
from flask_script import Manager, prompt_bool
from flask_migrate import Migrate, MigrateCommand


###load models to make flask migrate aware of them
from thermos.models import User, Bookmark, Tag, tags, Bookmark_flag
##########################

import random, pymysql
from datetime import datetime
from influxdb import InfluxDBClient

app = create_app(os.getenv('THERMOS_ENV') or 'mysql_statsd')                       # create thermos app instance
influx_client = InfluxDBClient(host='192.168.2.6',port=8086,database='telegraf')   # setup influxdb client
print ('THERMOS_ENV {} '.format(os.getenv('THERMOS_ENV')))

manager = Manager(app)                                                             # initialize manager

migrate = Migrate(app, db)                                                         # add DB management
manager.add_command('db', MigrateCommand)

# wrapper for influxdb's write method
def record_annotation(module,action,text):
    try:
        influx_client.write_points([{
            "measurement": "annotations",
            "tags": {"module": module,"action":action},
            "fields": {"text": text}
        }])
    except:
        print 'Unable to save annotation'

@manager.command
def insert_data():
    record_annotation(module="jobs", action="insert_data", text="Data initialization")
    def add_bookmark(user, url, description, tags):
        print 'adding bookmark user:{} url:{} desc:{} tags:{}'.format(user, url, description, tags)
        db.session.add(Bookmark(url=url, description=description, user=user, tags=tags))

    db.session.add(User(username="rjanuary", email="rjanuary@example.com", password="test"))
    db.session.add(User(username="user1", email="user1@example.com", password="user1"))
    db.session.add(User(username="user2", email="user2@example.com", password="user2"))
    db.session.add(User(username="user3", email="user3@example.com", password="user3"))
    db.session.add(User(username="user4", email="user4@example.com", password="user4"))
    db.session.add(Bookmark_flag(value=1))

    ins_user = User.get_by_username("rjanuary")

    add_bookmark(ins_user,'http://www.google.com','Google - Search Engine','search, all the stuff, yea!')
    add_bookmark(ins_user,'http://www.python.org','Primary Python site','programming,knowledge')

    db.session.commit()
    print 'Initialized the database'


@manager.command
def import_bookmarks(user_seed=0, poweruser_count=2000, max_bookmarks=300, total_record_count=500000):
    record_annotation(module="jobs",action="import_bookmarks", text="Bookmark Import Began")

    class fakeuser_factory(object):
        def __init__(self,user_seed=user_seed):
            self._user_count=int(user_seed)
        def usernumber(self):
            self._user_count += 1
            return self._user_count
        def create_user(self):
            username = 'user{}'.format(self.usernumber())
            if not User.query.filter_by(username=username).first():
                db.session.add(User(username=username, email="{}@example.com".format(username), password=username))
            else:
                print '{} already exists'.format(username)
            return User.get_by_username(username)

    uf = fakeuser_factory()

    user_record_count = int(poweruser_count)                                   #seed first user problems
    total_record_count = int(total_record_count)
    max_bookmarks=int(max_bookmarks)

    ins_user = uf.create_user()
    with open('./thermos/data/majestic_clean.csv') as f:
        next(f)
        for l in f:
            # print 't:{} u:{}'.format(total_record_count,user_record_count)
            total_record_count -= 1
            if total_record_count <= 0:
                print 'Hit maximum import limit of {}'.format(total_record_count)
                break                     #bail if we've hit our max record count
            if user_record_count <= 0:
                db.session.commit()
                user_record_count = random.randrange(1, max_bookmarks)
                ins_user = uf.create_user()
                # print 'created user:{} max bookmarks:{}'.format(ins_user.username,user_record_count)
            rank,rank2,url = l.split(',')
            db.session.add(Bookmark(url=url.strip(), description=url.strip(), user=ins_user, tags='imported'))
            # print 'inserted bookmark:{}'.format(url.strip())
            user_record_count -= 1
    db.session.commit()
    record_annotation(module="jobs", action="import_bookmarks", text="Bookmark Import Complete")

@manager.command
def dropdb():
    if prompt_bool(
        "Are you sure you want to lose all your data"):
        db.drop_all()
        record_annotation(module="jobs", action="dropdb", text="Database Drop confirmed")
        print 'Dropped the database'


@manager.command
def find_prime(count=100):
    print str(Bookmark_flag.find_next(int(count)))
    record_annotation(module="jobs", action="find_prime", text='found next {} primes'.format(count))


if __name__ == '__main__':
    manager.run()

