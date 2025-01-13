from datetime import datetime
from enum import Enum
from app import db


class TransactionStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELED = "canceled"
    EXPIRED = "expired"

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    balance = db.Column(db.Integer, nullable=False, default=0)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<User id={self.id} email={self.email}>"


class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    name = db.Column(db.String(255))
    price = db.Column(db.Integer, nullable=False)
    img = db.Column(db.String(255))
    category = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<Product id={self.id} name={self.name} price={self.price}>"


class Basket(db.Model):
    """
    - Поле user_id хранит id юзера
    -
    """
    __tablename__ = 'basket'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', onupdate="NO ACTION", ondelete="NO ACTION"), primary_key=True, unique=True)
    products_id = db.Column(db.JSON, nullable=False)

    user = db.relationship('User', backref=db.backref('basket', uselist=False))

    def __repr__(self):
        return f"<Basket user_id={self.user_id} products_id={self.products_id}>"