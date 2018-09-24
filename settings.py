import os

POSTGRES = {
    'user': os.environ.get('POSTGRES_USER'),
    'pw': os.environ.get('POSTGRES_USER_PWD'),
    'db': os.environ.get('POSTGRES_DB_NAME'),
    'host': os.environ.get('POSTGRES_HOST'),
    'port': os.environ.get('POSTGRES_PORT'),
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
