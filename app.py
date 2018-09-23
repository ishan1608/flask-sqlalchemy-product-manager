import json
import logging
import os

from flask import Flask, render_template, request, redirect, jsonify, Response
from flask_restful import Api
from sqlalchemy import inspect, or_, desc

import settings
from api import BookResource, BookResourceList, ProductResource, ProductResourceList, WebhookConfigResource
from flask_tus import tus_manager
from models import db, Book

logging.basicConfig(filename='default.log', level=logging.DEBUG)

project_dir = os.path.dirname(os.path.abspath(__file__))


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = settings.DATABASE_URL
    # Disable soon to be deprecated signals
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config['CELERY_BROKER_URL'] = settings.CELERY['CELERY_BROKER_URL']
    app.config['CELERY_RESULT_BACKEND'] = settings.CELERY['CELERY_RESULT_BACKEND']

    db.init_app(app)
    return app


def get_db():
    return db


app = create_app()
api = Api(app)

api.add_resource(ProductResource, '/product/<int:product_id>/')
api.add_resource(ProductResourceList, '/product/')
api.add_resource(WebhookConfigResource, '/webhook-config/')


@app.route('/products/search/', methods=['GET'])
def products_search():
    from models import Product

    query = request.args.get('query', '')
    field = request.args.get('field')
    offset = int(request.args.get('offset', 0))
    limit = int(request.args.get('limit', 10))

    if offset < 0 or limit <= 0:
        return Response(
            response=json.dumps(dict(description='Invalid offset or limit')),
            status=400,
            mimetype='application/json'
        )

    searchable_fields = [field.key for field in inspect(Product).attrs if field.key not in ['id', 'is_active']]
    if field and field not in searchable_fields:
        return Response(
            response=json.dumps(dict(description='Field: "{}" is not valid'.format(field))),
            status=400,
            mimetype='application/json'
        )

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


##################################
# Product Pages
##################################


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/products/active', methods=['GET'])
def products_active():
    return render_template('products_paginated.html', active_mode=True)


@app.route('/products/inactive', methods=['GET'])
def products_inactive():
    return render_template('products_paginated.html', active_mode=False)


@app.route('/products/create', methods=['GET'])
def products_create():
    return render_template('products_create.html')


##################################
# Import
##################################


tm = tus_manager(app, upload_url='/products-csv-upload', upload_folder='uploads/')


@tm.upload_file_handler
def upload_file_hander(upload_file_path, filename):
    from celery_tasks import process_csv

    if settings.CELERY_ENABLED:
        process_csv.apply_async(args=[upload_file_path], queue='flask-crud-celery')
    else:
        process_csv(upload_file_path)
    return filename


@app.route('/products/import/', methods=['GET'])
def products_import():
    return render_template('products_import.html', tm=tm)


##################################
# BOOKS
##################################


api.add_resource(BookResource, '/book/<int:book_id>/')
api.add_resource(BookResourceList, '/book/')


@app.route('/books', methods=['GET'])
def books_index():
    books = Book.query.all()
    return render_template('books-index.html', books=books)


@app.route('/books/create', methods=['POST'])
def books_create():
    try:
        book = Book(title=request.form.get('title'))
        db.session.add(book)
        db.session.commit()
    except Exception as e:
        app.logger.error('Failed to add book')
        app.logger.error(e)
    return redirect('/books')


@app.route('/books/update', methods=['POST'])
def books_update():
    try:
        new_title = request.form.get('newtitle')
        old_title = request.form.get('oldtitle')
        book = Book.query.filter_by(title=old_title).first()
        book.title = new_title
        db.session.commit()
    except Exception as e:
        app.logger.error("Couldn't update book title")
        app.logger.error(e)
    return redirect('/books')


@app.route('/books/delete', methods=['POST'])
def books_delete():
    title = request.form.get('title')
    book = Book.query.filter_by(title=title).first()
    db.session.delete(book)
    db.session.commit()
    return redirect('/books')


if __name__ == '__main__':
    app.run(debug=True)
