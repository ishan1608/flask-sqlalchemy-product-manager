import csv

from celery import Celery
from sqlalchemy.exc import IntegrityError

from app import create_app


def make_celery(app):
    celery = Celery(app.import_name, backend=app.config['CELERY_RESULT_BACKEND'], broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)

    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask

    celery.conf.update({
        'CELERY_DEFAULT_QUEUE': 'flask-crud-celery',
    })
    return celery


app = create_app()
celery = make_celery(app)


@celery.task
def process_csv(file_path):
    from models import Product
    from app import get_db

    db = get_db()

    with open(file_path, "r") as products_csv_file:
        products_reader = csv.reader(products_csv_file)
        next(products_reader)
        for product_row in products_reader:
            try:
                product = Product(
                    name=product_row[0],
                    sku=product_row[1],
                    description=product_row[2],
                    is_active=True
                )
                db.session.add(product)
                db.session.commit()
            except IntegrityError as error:
                print('==========================================================================================================')
                print(error)
                print('==========================================================================================================')
                db.session.rollback()
            except Exception as exception:
                app.logger.error(exception)


@celery.task
def post_product_webhook(product_id, action):
    from api import ProductResource

    ProductResource.post_product_webhook(product_id, action)
