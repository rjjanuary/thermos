import os
from thermos import create_app, db

from flask_script import Manager, prompt_bool
from flask_migrate import Migrate, MigrateCommand

###load models to make flask migrate aware of them
from thermos.models import User, Bookmark, Tag, tags
##########################

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
        db.session.add(Bookmark(url=url, description=description, user=user,
                                tags=tags))
        print 'adding tags'
        for name in ['python','search','knowledge','notused']:
            print 'tag: {}'.format(name)
            db.session.add(Tag(name))

    db.session.add(User(username="rjanuary", email="rjanuary@example.com", password="test"))
    db.session.add(User(username="other", email="other@example.com", password="test"))
    ins_user = User.get_by_username("rjanuary")

    add_bookmark(ins_user,'http://www.google.com','Google - Search Engine','search')
    add_bookmark(ins_user,'http://www.python.org','Python homepage','programming,knowledge')

    db.session.commit()
    print 'Initialized the database'


@manager.command
def dropdb():
    if prompt_bool(
        "Are you sure you want to lose all your data"):
        db.drop_all()
        print 'Dropped the database'

if __name__ == '__main__':
    manager.run()

