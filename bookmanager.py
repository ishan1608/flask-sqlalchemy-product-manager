import os

from flask import Flask, render_template, request, redirect

from models import db, Book

project_dir = os.path.dirname(os.path.abspath(__file__))
POSTGRES = {
    'user': 'ishan',
    'pw': '612189@p3',
    'db': 'flask-crud',
    'host': 'localhost',
    'port': '5432'
}

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES
# Disable soon to be deprecated signals
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


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


if __name__ == '__main__':
    app.run(debug=True)
