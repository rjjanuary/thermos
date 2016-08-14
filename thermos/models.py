from datetime import datetime
from sqlalchemy import desc
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from . import stats_client
from . import db

tags = db.Table('bookmark_tag',
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
    db.Column('bookmark_id', db.Integer, db.ForeignKey('bookmark.id'))
)


class Bookmark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.String(300))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)
    _tags = db.relationship('Tag', secondary=tags, lazy='joined',
                            backref=db.backref('bookmarks', lazy='dynamic'))

    def __init__(self, **kwargs):
        super(Bookmark, self).__init__(**kwargs)
        stats_client.incr('thermos.models,type=bookmark')

    @staticmethod
    def newest(num):
        return Bookmark.query.order_by(desc(Bookmark.date)).limit(num)

    @property
    def tags(self):
        return ",".join([t.name for t in self._tags])

    @tags.setter
    def tags(self, string):
        if string:
            self._tags = [Tag.get_or_create(name) for name in string.split(',')]
        else:
            self._tags = []

    def __repr__(self):
        return "<Bookmark '{}': '{}'>".format(self.description, self.url)


class User(db.Model, UserMixin):
    #^UserMixin from flask_login exposes methods to determine auth state
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    bookmarks = db.relationship('Bookmark', backref='user', lazy='dynamic')
    password_hash = db.Column(db.String(80))

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        stats_client.incr('thermos.models,type=user')

    @property
    def password(self):
        raise AttributeError('password: write-only field')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self,password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def get_by_username(username):
        return User.query.filter_by(username=username).first()

    def __repr__(self):
        return '<User %r>' % self.username


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), nullable=False, unique=True, index=True)

    def __init__(self, **kwargs):
        super(Tag, self).__init__(**kwargs)
        stats_client.incr('thermos.models,type=tag')

    @staticmethod
    def get_or_create(name):
        name = name.strip()
        try:
            return Tag.query.filter_by(name=name).one()
        except:
            return Tag(name=name)

    @staticmethod
    def all():
        return Tag.query.all()

    def __repr__(self):
        return self.name


class Bookmark_flag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer, nullable=False, unique=True)

    def __init__(self, **kwargs):
        super(Bookmark_flag, self).__init__(**kwargs)
        stats_client.incr('thermos.models,type=bookmark_flag')

    @staticmethod
    def find_next(count=1):
        def isp(nbr):
            for i in range(2,nbr-1):
                if nbr%i == 0:
                    return False
            return True

        last_result = db.session.query(db.func.max(Bookmark_flag.value)).first()
        nbr=last_result[0]
        print "last nbr is:{}".format(nbr)
        while count >= 0:
            while True:
                nbr += 1
                if isp(nbr):
                    db.session.add(Bookmark_flag(value=nbr))
                    count -= 1
                    found=nbr
                    break
        db.session.commit()
        return found

    def __repr__(self):
        return self.value