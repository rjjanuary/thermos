import os, sys

PROJECT_DIR = '/var/www/thermos/'
sys.path.append(PROJECT_DIR)

from thermos import create_app
application = create_app(os.getenv('THERMOS_ENV') or 'mysql_statsd')