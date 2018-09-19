from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class BaseModel(db.Model):
    """Base Model with incrementing ID"""
    id = db.Column(db.Integer, primary_key=True)

    __abstract__ = True

    def json(self):
        """Base way to jsonify models, dealing with datetime objects"""
        return {
            column: value if not isinstance(value, datetime.date) else value.strftime('%Y-%m-%d')
            for column, value in self._to_dict().items()
        }


class Book(BaseModel):
    title = db.Column(db.String(128), unique=True, nullable=False)

    def __repr__(self):
        return '<Title: {}>'.format(self.title)
