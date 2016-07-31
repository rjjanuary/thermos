import os
from thermos import create_app, db

from flask_script import Manager, prompt_bool
from flask_migrate import Migrate, MigrateCommand

###load models to make flask migrate aware of them
from thermos.models import User, Bookmark, Tag, tags
##########################

app = create_app(os.getenv('THERMOS_ENV') or 'dev')

manager = Manager(app)

migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)

@manager.command
def insert_data():
    db.create_all()
    db.session.add(User(username="rjanuary", email="rjanuary@example.com", password="test"))
    db.session.add(User(username="other", email="other@example.com", password="test"))

    def add_bookmark(url, description, tags):
        db.session.add(Bookmark(url=url, description=description, user="rjanuary",
                                tags=tags))
    for name in ['python','search','knowledge','notused']:
        db.session.add(Tag(name))

    db.session.commit()

    add_bookmark('http://www.google.com','Google - Search Engine','search')
    add_bookmark('http://www.python.org','Python homepage','programming,knowledge')

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
