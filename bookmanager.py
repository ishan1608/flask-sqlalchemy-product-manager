import os

from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = 'sqlite:///{}'.format(os.path.join(project_dir, 'book_database.db'))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = database_file

db = SQLAlchemy(app)


@app.route('/', methods=['GET', 'POST', 'OPTIONS'])
def home():
    if request.form:
        print(request.form)
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
