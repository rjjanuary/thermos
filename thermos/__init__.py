import os

from flask import Flask, request #, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy, get_debug_queries
from flask_login import LoginManager
from flask_moment import Moment
from flask_debugtoolbar import DebugToolbarExtension
from flask_metrics import statsd_middleware, StatsClient, Annotator

from .config import config_by_name

db = SQLAlchemy()                                   # create instance of SQLAlchemy ORM engine
stats_client = StatsClient()                        # create instance of our app level statsd client
annotator = Annotator()

#Configure Authentication
login_manager=LoginManager()                        # begin to configure authentication
login_manager.session_protection = "strong"
login_manager.login_view = "auth.login"             # set where to send people needing to log in


toolbar = DebugToolbarExtension()                   # enable the debug toolbar (found on right when debug=true)
moment = Moment()                                   # framework taking timestamps and converting to '2 hours ago'


def create_app(config_name):                        # app factory, generating our application object
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    db.init_app(app)
    login_manager.init_app(app)
    moment.init_app(app)
    toolbar.init_app(app)

    stats_client.init_app(app)                      # initialize our statsd client, assign it within app
    annotator.init_app(app)                         # initialize our annotator, assign it within app
    app.wsgi_app = statsd_middleware(app)           # initialize our statsd middleware
    # annotator.write(module='app',action='startup',text='application initialized')

    from .main import main as main_blueprint        # blueprints are self contained portions of an application
    app.register_blueprint(main_blueprint, url_prefix='/')

    from .bookmarks import bookmarks as bkm_blueprint
    app.register_blueprint(bkm_blueprint, url_prefix='/bookmarks')

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    @app.after_request                              # sql records are available up until the end of the request
    def after_request(response):                    # hook into 'after request' allowing us to send to statsd
        if app.config['SQLALCHEMY_RECORD_QUERIES']:
            queries = get_debug_queries()
            for query in queries:
                context=query.context.replace(':','_')
                print context
                duration = query.duration * 1000 #convert to ms
                app.stats_client.timing('thermos.queries,context={},path={}'.format(context,request.path),duration)
                print (query.duration)
            return response

    return app


