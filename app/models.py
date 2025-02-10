from app import db
from flask_login import UserMixin
from datetime import datetime


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    products = db.Column(db.Text, nullable=False)  # Список товаров в JSON-формате
    total_amount = db.Column(db.Float, nullable=False)
    address = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='orders', lazy=True)


class User(db.Model, UserMixin):
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
    __tablename__ = 'basket'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', onupdate="NO ACTION", ondelete="NO ACTION"), primary_key=True, unique=True)
    products_id = db.Column(db.JSON, nullable=False)

    user = db.relationship('User', backref=db.backref('basket', uselist=False))

    def __repr__(self):
        return f"<Basket user_id={self.user_id} products_id={self.products_id}>"


class Sticker(db.Model):
    __tablename__ = 'stickers'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    description = db.Column(db.String(500), nullable=False)  # Описание для генерации
    image_url = db.Column(db.String(500), nullable=False)    # Ссылка на сгенерированное изображение
    price = db.Column(db.Float, nullable=False, default=100) # Цена наклейки
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Кто создал
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='stickers')

    def __repr__(self):
        return f"<Sticker id={self.id} description={self.description}>"