from flask import request, abort
from flask_restful import Resource
from sqlalchemy import desc

from models import db, Book, Product


class BookResource(Resource):
    def get(self, book_id):
        book = Book.query.filter_by(id=book_id).first()
        if not book:
            abort(404, {
                'message': 'Book: {} Not Found'.format(book_id)
            })
        return book.json()

    def put(self, book_id):
        book = Book.query.filter_by(id=book_id).first()
        if not book:
            abort(404, {
                'message': 'Book: {} Not Found'.format(book_id)
            })
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
            abort(400, {
                'message': 'Title cannot be blank'
            })
        book = Book(title=title)
        db.session.add(book)
        db.session.commit()
        return book.json()


class ProductResource(Resource):
    def get(self, product_id):
        product = Product.query.filter_by(id=product_id).first()
        if not product:
            abort(404, {
                'message': 'Product: {} Not Found'.format(product_id)
            })
        return product.json()

    def put(self, product_id):
        product = Product.query.filter_by(id=product_id).first()
        if not product:
            abort(404, {
                'message': 'Product: {} Not Found'.format(product_id)
            })
        product.sku = request.form.get('sku', product.sku)
        product.name = request.form.get('name', product.name)
        product.description = request.form.get('description', product.description)
        product.is_active = request.form.get('is_active', product.is_active)
        db.session.commit()
        return product.json()


class ProductResourceList(Resource):
    def get(self):
        offset = int(request.args.get('offset', 0))
        limit = int(request.args.get('limit', 10))

        total_products_count = Product.query.count()

        if total_products_count <= offset:
            abort(404, {
                'message': 'No more products found'
            })

        products = [product.json() for product in Product.query.order_by(desc(Product.id)).slice(offset, offset + limit)]
        return {
            'meta': {
                'count': len(products),
                'total_count': total_products_count
            },
            'objects': products
        }

    def post(self):
        sku = request.form.get('sku')
        name = request.form.get('name')
        description = request.form.get('description', '')
        is_active = request.form.get('is_active', True)
        if not sku:
            abort(400, {
                'message': 'SKU cannot be blank'
            })
        if not name:
            abort(400, {
                'message': 'Name cannot be blank'
            })
        product = Product(
            sku=sku,
            name=name,
            description=description,
            is_active=is_active
        )
        db.session.add(product)
        db.session.commit()
        return product.json()
