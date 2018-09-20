import logging
import os

from flask import Flask, render_template, request, redirect, abort, jsonify
from flask_restful import Api
from sqlalchemy import inspect, or_, desc

from api import BookResource, BookResourceList, ProductResource, ProductResourceList, WebhookConfigResource
from flask_tus import tus_manager
from models import db, Book

logging.basicConfig(filename='default.log', level=logging.DEBUG)

CELERY_ENABLED = True

project_dir = os.path.dirname(os.path.abspath(__file__))
POSTGRES = {
    'user': 'ishan',
    'pw': '612189@p3',
    'db': 'flask-crud',
    'host': 'localhost',
    'port': '5432'
}


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES
    # Disable soon to be deprecated signals
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379'
    app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379'

    db.init_app(app)
    return app


def get_db():
    return db


app = create_app()
api = Api(app)

tm = tus_manager(app, upload_url='/products-csv-upload', upload_folder='uploads/')


@tm.upload_file_handler
def upload_file_hander(upload_file_path, filename):
    from celery_tasks import process_csv

    if CELERY_ENABLED:
        process_csv.apply_async(args=[upload_file_path], queue='flask-crud-celery')
    else:
        process_csv(upload_file_path)
    return filename


api.add_resource(BookResource, '/book/<int:book_id>/')
api.add_resource(BookResourceList, '/book/')
api.add_resource(ProductResource, '/product/<int:product_id>/')
api.add_resource(ProductResourceList, '/product/')
api.add_resource(WebhookConfigResource, '/webhook-config/')


@app.route('/', methods=['GET'])
def home():
    books = Book.query.all()
    return render_template('index.html', books=books)


@app.route('/create', methods=['POST'])
def create():
    try:
        book = Book(title=request.form.get('title'))
        db.session.add(book)
        db.session.commit()
    except Exception as e:
        app.logger.error('Failed to add book')
        app.logger.error(e)
    return redirect('/')


@app.route('/update', methods=['POST'])
def update():
    try:
        new_title = request.form.get('newtitle')
        old_title = request.form.get('oldtitle')
        book = Book.query.filter_by(title=old_title).first()
        book.title = new_title
        db.session.commit()
    except Exception as e:
        app.logger.error("Couldn't update book title")
        app.logger.error(e)
    return redirect('/')


@app.route('/delete', methods=['POST'])
def delete():
    title = request.form.get('title')
    book = Book.query.filter_by(title=title).first()
    db.session.delete(book)
    db.session.commit()
    return redirect('/')


@app.route('/product/import/', methods=['GET'])
def products_import():
    return render_template('products_import.html', tm=tm)


@app.route('/product/search/', methods=['GET'])
def products_search():
    from models import Product

    query = request.args.get('query', '')
    field = request.args.get('field')
    offset = int(request.args.get('offset', 0))
    limit = int(request.args.get('limit', 10))

    if offset < 0 or limit <= 0:
        abort(400, {
            'message': 'Invalid offset or limit'
        })

    searchable_fields = [field.key for field in inspect(Product).attrs if field.key not in ['id', 'is_active']]
    if field and field not in searchable_fields:
        abort(400, {
            'message': 'Field: {} is not valid'.format(field)
        })
    if not field:
        products = Product.query.order_by(Product.id).filter(or_(
            Product.name.contains(query),
            Product.sku.contains(query),
            Product.description.contains(query)
        ))
    else:
        products = Product.query.order_by(desc(Product.id)).filter(getattr(Product, field).contains(query))

    total_products_count = products.count()
    products = [product.json() for product in products.slice(offset, offset + limit)]
    return jsonify({
        'meta': {
            'count': len(products),
            'total_count': total_products_count,
            'previous': '/product/?offset={}&limit={}'.format(offset - limit, limit) if (offset - limit) >= 0 else None,
            'next': '/product/?offset={}&limit={}'.format(offset + limit, limit) if (offset + limit) < total_products_count else None
        },
        'objects': products
    })


if __name__ == '__main__':
    app.run(debug=True)
