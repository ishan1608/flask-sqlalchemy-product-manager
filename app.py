import os

from flask import Flask, render_template, request, redirect
from flask_restful import Api

from api import BookResource, BookResourceList, ProductResource, ProductResourceList
from flask_tus import tus_manager
from models import db, Book

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
        print('Failed to add book')
        print(e)
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
        print("Couldn't update book title")
        print(e)
    return redirect('/')


@app.route('/delete', methods=['POST'])
def delete():
    title = request.form.get('title')
    book = Book.query.filter_by(title=title).first()
    db.session.delete(book)
    db.session.commit()
    return redirect('/')


@app.route('/products/import/', methods=['GET'])
def products_import():
    return render_template('products_import.html', tm=tm)


if __name__ == '__main__':
    app.run(debug=True)
