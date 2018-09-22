POSTGRES = {
    'user': 'ishan',
    'pw': '612189@p3',
    'db': 'flask-crud',
    'host': 'localhost',
    'port': '5432'
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
