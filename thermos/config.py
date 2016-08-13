import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = '\xf7]\x88\x89\x8a\xd8\x99\x0cf\x91\xc9c\x9f\n\x03\x9f8\xadA\xd2\xfc\xf5\x17\x0e'
    DEBUG = False
    SQLALCHEMY_RECORD_QUERIES = False
    STATSD_HOST = '10.162.2.121'
    STATSD_PORT = 8125

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'thermos.db')

class DevelopmentStatsD(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'thermos.db')
    SQLALCHEMY_RECORD_QUERIES = True
    # STATSD_HOST = 'nic-vtxprd-oradb04'
    # STATSD_PORT = 8125

class TestingConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'thermos.db')

class MySQLConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://thermos:thermos@localhost/thermos'

class MySQLStatsD(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://thermos:thermos@localhost/thermos'
    SQLALCHEMY_RECORD_QUERIES = True
    # STATSD_HOST = '<insert_metric_host>'
    # STATSD_PORT = 8125

config_by_name = dict(
    dev = DevelopmentConfig,
    test = TestingConfig,
    prod = ProductionConfig,
    mysql = MySQLConfig,
    mysql_statsd = MySQLStatsD,
    dev_statsd = DevelopmentStatsD
)