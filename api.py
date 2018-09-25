import pickledb
import requests
from flask import request, abort, make_response, url_for
from flask_restful import Resource
from sqlalchemy import desc

import settings
from models import db, Book, Product
from util import url_validator

config_db = pickledb.load(settings.CONFIG_DB, False)


class ProductResource(Resource):
    def get(self, product_id):
        product = Product.query.filter_by(id=product_id).first()
        if not product:
            abort(404, description='Product: {} Not Found'.format(product_id))
        return product.json()

    def put(self, product_id):
        from celery_tasks import post_product_webhook

        product = Product.query.filter_by(id=product_id).first()
        if not product:
            abort(404, description='Product: {} Not Found'.format(product_id))
        product.sku = request.form.get('sku', product.sku)
        product.name = request.form.get('name', product.name)
        product.description = request.form.get('description', product.description)
        is_active = request.form.get('is_active')
        product.is_active = product.is_active if not is_active else is_active.lower() == 'true'
        db.session.commit()

        # Trigger Webhook
        action = 'update'
        if settings.CELERY_ENABLED:
            post_product_webhook.apply_async(args=[product.id, action], queue='flask-crud-celery')
        else:
            self.post_product_webhook(product.id, action)

        return product.json()

    @classmethod
    def post_product_webhook(cls, product_id, action):
        product = Product.query.get(product_id)
        payload = {
            'action': action,
            'object': product.json()
        }
        webhook_config_url = config_db.get('webhook_config')
        print('webhook-config')
        print(webhook_config_url)
        if not webhook_config_url:
            return

        if action == 'update':
            requests.put(webhook_config_url, json=payload)
        else:
            requests.post(webhook_config_url, json=payload)


class ProductResourceList(Resource):
    def head(self):
        active_products_count = Product.query.filter_by(is_active=True).count()
        inactive_products_count = Product.query.filter_by(is_active=False).count()
        resp = make_response()
        resp.headers['TOTAL_COUNT'] = active_products_count + inactive_products_count
        resp.headers['ACTIVE_COUNT'] = active_products_count
        resp.headers['INACTIVE_COUNT'] = inactive_products_count
        return resp

    def get(self):
        offset = int(request.args.get('offset', 0))
        limit = int(request.args.get('limit', 10))
        is_active = request.args.get('is_active')

        if offset < 0 or limit <= 0:
            abort(400, description='Invalid offset or limit')

        products = Product.query.order_by(desc(Product.id))
        if is_active is not None:
            is_active = False if is_active.lower() == 'false' else True
            products = products.filter_by(is_active=is_active)

        total_products_count = products.count()

        products = [product.json() for product in products.slice(offset, offset + limit)]
        return {
            'meta': {
                'count': len(products),
                'offset': offset,
                'total_count': total_products_count,
                'previous': '{}?offset={}&limit={}'.format(url_for('productresourcelist'), offset - limit, limit) if (offset - limit) >= 0 else None,
                'next': '{}?offset={}&limit={}'.format(url_for('productresourcelist'), offset + limit, limit) if (offset + limit) < total_products_count else None
            },
            'objects': products
        }

    def post(self):
        from celery_tasks import post_product_webhook

        sku = request.form.get('sku')
        name = request.form.get('name')
        description = request.form.get('description', '')
        is_active = request.form.get('is_active')
        is_active = True if not is_active else is_active.lower() == 'true'

        if not sku:
            abort(400, description='SKU cannot be blank')
        if not name:
            abort(400, description='Name cannot be blank')
        product = Product(
            sku=sku,
            name=name,
            description=description,
            is_active=is_active
        )
        db.session.add(product)
        db.session.commit()

        # Trigger Webhook
        action = 'create'
        if settings.CELERY_ENABLED:
            post_product_webhook.apply_async(args=[product.id, action], queue='flask-crud-celery')
        else:
            post_product_webhook(product.id, action)

        return product.json()


class WebhookConfigResource(Resource):
    def get(self):
        url = config_db.get('webhook_config')
        return {
            'object': url
        }

    def post(self):
        url = request.form.get('url')
        if not url_validator(url):
            abort(400, description='Invalid URL')

        config_db.set('webhook_config', url)
        config_db.dump()
        return {
            'object': url
        }

##################################
# BOOKS
##################################


class BookResource(Resource):
    def get(self, book_id):
        book = Book.query.filter_by(id=book_id).first()
        if not book:
            abort(404, description='Book: {} Not Found'.format(book_id))
        return book.json()

    def put(self, book_id):
        book = Book.query.filter_by(id=book_id).first()
        if not book:
            abort(404, description='Book: {} Not Found'.format(book_id))
        title = request.form.get('title')
        book.title = title
        db.session.commit()
        return book.json()


class BookResourceList(Resource):
    def get(self):
        books = [book.json() for book in Book.query.all()]
        return {
            'count': len(books),
            'objects': books
        }

    def post(self):
        title = request.form.get('title')
        if not title:
            abort(400, description='Title cannot be blank')
        book = Book(title=title)
        db.session.add(book)
        db.session.commit()
        return book.json()
