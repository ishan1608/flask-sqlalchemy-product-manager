import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class BaseModel(db.Model):
    """Base Model with incrementing ID"""
    id = db.Column(db.Integer, primary_key=True)

    __abstract__ = True

    def _to_dict(self):
        return {
            'id': self.id
        }

    def json(self):
        """Base way to jsonify models, dealing with datetime objects"""
        return {
            column: value if not isinstance(value, datetime.date) else value.strftime('%Y-%m-%d')
            for column, value in self._to_dict().items()
        }


class Book(BaseModel):
    title = db.Column(db.String(128), unique=True, nullable=False)

    def _to_dict(self):
        dictionary = super()._to_dict()
        dictionary.update({
            'title': self.title
        })
        return dictionary

    def __repr__(self):
        return '<Title: {}>'.format(self.title)


class Product(BaseModel):
    sku = db.Column(db.String(64), unique=True, nullable=False)
    name = db.Column(db.String(256), unique=False, nullable=False)
    description = db.Column(db.Text())
    is_active = db.Column(db.Boolean())

    def _to_dict(self):
        dictionary = super()._to_dict()
        dictionary.update({
            'sku': self.sku,
            'name': self.name,
            'description': self.description,
            'is_active': self.is_active,
        })
        return dictionary

    def __repr__(self):
        return '<sku: {}>'.format(self.sku)
