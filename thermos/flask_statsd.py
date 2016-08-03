'''
http://werkzeug.pocoo.org/docs/0.11/routing/
https://ohadp.com/adding-a-simple-middleware-to-your-flask-application-in-1-minutes-89782de379a1#.6vwkw18f3
http://steinn.org/post/flask-statsd/                                                    #implement statsd in flask
http://eddmann.com/posts/creating-a-basic-auth-wsgi-middleware-in-python/               #create middleware
http://flask.pocoo.org/docs/0.11/api/
http://flask.pocoo.org/snippets/53/                                                     #after_request

'''
from statsd import StatsClient as base_statsd
from time import time, sleep
from flask_sqlalchemy import get_debug_queries


class StatsClient(base_statsd):
    def __init__(self, app=None):
        if app:
            self.init_app(app)
    def init_app(self,app):
        super(StatsClient,self).__init__(
            host=app.config['STATSD_HOST'],
            port=app.config['STATSD_PORT'])
        app.stats_client=self

class FlaskTimer(object):
    def __init__(self, app, tags=None):
        self.app=app
        if tags is None:
            tags = {}
        self.tags = tags
    def addTag(self,TagKey,TagValue):
        self.tags[TagKey]=TagValue
    @property
    def time(self):
        return (self.end_time-self.start_time)*1000    #return ms between start and end
    def __enter__(self):
        self.start_time=time()
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        self.end_time=time()
        tagstr= ",".join(["=".join([key, str(val)]) for key, val in self.tags.items()])
        self.app.stats_client.timing('{},{}'.format(self.app.name,tagstr),self.time)
        # print 'stat: {},{}'.format(self.app.name, tagstr)

class statsd_middleware(object):
    def __init__(self,app):
        self.app = app
        self.wsgi_app = app.wsgi_app
        self.map = app.url_map.bind('')
        self.statsd_client=StatsClient(self.app)

    def __call__(self,environ, start_response):
        def start_response_wrapper(*args, **kwargs):
            status = args[0].split(' ')[0]
            self.status = status
            return start_response(*args, **kwargs)

        # try:
        with FlaskTimer(self.app) as ft:
            response = self.wsgi_app(environ, start_response_wrapper)
            ft.addTag("path",environ['PATH_INFO'])
            ft.addTag("request_type", environ['REQUEST_METHOD'])
            ft.addTag("status_code",self.status)

        # except Exception:
        #     return self.wsgi_app(environ, start_response)
        return response

# @app.after_request  # sql records are available up until the end of the request
# def after_request(response):  # hook into 'after request' allowing us to send to statsd
#     if app.config['SQLALCHEMY_RECORD_QUERIES']:
#         queries = get_debug_queries()
#         for query in queries:
#             print (query.duration)
#         return response