import os

POSTGRES = {
    'user': os.environ['POSTGRES_USER'],
    'pw': os.environ['POSTGRES_USER_PWD'],
    'db': os.environ['POSTGRES_DB_NAME'],
    'host': os.environ['POSTGRES_HOST'],
    'port': os.environ['POSTGRES_PORT'],
}

DATABASE_URL = (
    'postgresql://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES
)

CELERY = {
    'CELERY_BROKER_URL': 'redis://localhost:6379',
    'CELERY_RESULT_BACKEND': 'redis://localhost:6379',
}

CELERY_ENABLED = True

CONFIG_DB = 'config.db'

# Importing local_settings.py
try:
    from local_settings import *
except:
    pass
