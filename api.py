from flask import request, abort
from flask_restful import Resource

from models import db, Book


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
            abort(404, {
                'message': 'Title cannot be blank'
            })
        book = Book(title=title)
        db.session.add(book)
        db.session.commit()
        return book.json()
