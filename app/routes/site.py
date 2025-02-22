import os

from flask import Blueprint, request, redirect, url_for, render_template, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app import db
from app.models import Product, Basket, Order
from ..utils import generate_sticker, allowed_file
import json
import random

bp = Blueprint('site', __name__)

@bp.route('/site')
def main_page():
    return render_template('main_page.html')

@bp.route('/catalog/<category>')
def catalog(category):
    products = Product.query.filter_by(category=category).all()
    return render_template('catalog.html', products=products, category=category)

@bp.route('/add_to_cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    basket = Basket.query.filter_by(user_id=current_user.id).first()

    if not basket:
        # Если корзины нет, создаем новую
        basket = Basket(user_id=current_user.id, products_id=json.dumps([]))
        db.session.add(basket)

    # Получаем текущий список товаров
    products = json.loads(basket.products_id)

    # Проверяем, есть ли товар уже в корзине
    product_in_cart = next((item for item in products if item['id'] == product_id), None)

    if product_in_cart:
        # Если товар уже в корзине, увеличиваем количество
        product_in_cart['quantity'] += 1
    else:
        # Если товара нет, добавляем его
        products.append({'id': product_id, 'quantity': 1})

    # Обновляем корзину
    basket.products_id = json.dumps(products)
    db.session.commit()

    flash('Товар добавлен в корзину!', 'success')
    return redirect(url_for('site.catalog', category=product.category))

@bp.route('/add_sticker_to_cart/<int:sticker_id>', methods=['POST'])
@login_required
def add_sticker_to_cart(sticker_id):
    product = Product.query.get_or_404(sticker_id)
    basket = Basket.query.filter_by(user_id=current_user.id).first()

    if not basket:
        # Если корзины нет, создаем новую
        basket = Basket(user_id=current_user.id, products_id=json.dumps([]))
        db.session.add(basket)

    # Получаем текущий список товаров
    products = json.loads(basket.products_id)

    # Проверяем, есть ли товар уже в корзине
    product_in_cart = next((item for item in products if item['id'] == sticker_id), None)

    if product_in_cart:
        # Если товар уже в корзине, увеличиваем количество
        product_in_cart['quantity'] += 1
    else:
        # Если товара нет, добавляем его
        products.append({'id': sticker_id, 'quantity': 1})

    # Обновляем корзину
    basket.products_id = json.dumps(products)
    db.session.commit()

    flash('Товар добавлен в корзину!', 'success')
    return redirect(url_for('site.catalog', category=product.category))

@bp.route('/cart')
@login_required
def cart():
    basket = Basket.query.filter_by(user_id=current_user.id).first()

    if not basket or not basket.products_id:
        return render_template('cart.html', cart_items=[], total_amount=0)

    # Получаем товары из корзины
    products_in_cart = json.loads(basket.products_id)
    cart_items = []

    total_amount = 0
    for item in products_in_cart:
        product = Product.query.get(item['id'])
        if product:
            cart_items.append({
                'product': product,
                'quantity': item['quantity']
            })
            total_amount += product.price * item['quantity']

    return render_template('cart.html', cart_items=cart_items, total_amount=total_amount)

@bp.route('/remove_from_cart/<int:product_id>', methods=['POST'])
@login_required
def remove_from_cart(product_id):
    basket = Basket.query.filter_by(user_id=current_user.id).first()

    if not basket or not basket.products_id:
        flash('Корзина пуста!', 'error')
        return redirect(url_for('site.cart'))

    # Получаем текущий список товаров
    products = json.loads(basket.products_id)

    # Удаляем товар из корзины
    products = [item for item in products if item['id'] != product_id]

    # Обновляем корзину
    basket.products_id = json.dumps(products)
    db.session.commit()

    flash('Товар удалён из корзины!', 'success')
    return redirect(url_for('site.cart'))

@bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    basket = Basket.query.filter_by(user_id=current_user.id).first()

    if not basket or not basket.products_id:
        flash('Ваша корзина пуста!', 'error')
        return redirect(url_for('site.cart'))

    if request.method == 'POST':
        address = request.form.get('address')

        # Получаем товары из корзины
        products_in_cart = json.loads(basket.products_id)
        total_amount = 0
        order_items = []

        for item in products_in_cart:
            product = Product.query.get(item['id'])
            if product:
                total_amount += product.price * item['quantity']
                order_items.append({
                    'id': product.id,
                    'name': product.name,
                    'price': product.price,
                    'quantity': item['quantity']
                })

        # Проверяем, достаточно ли средств у пользователя
        if current_user.balance < total_amount:
            flash('Недостаточно средств на балансе', 'error')
            return redirect(url_for('site.cart'))

        try:
            # Создаем новый заказ
            new_order = Order(
                user_id=current_user.id,
                products=json.dumps(order_items),
                total_amount=total_amount,
                address=address
            )
            db.session.add(new_order)

            # Списание средств с баланса пользователя
            current_user.balance -= total_amount

            # Очищаем корзину
            basket.products_id = json.dumps([])
            db.session.commit()

            flash(f'Заказ успешно оформлен на сумму {total_amount} руб.!', 'success')
            return redirect(url_for('site.main_page'))
        except Exception as e:
            db.session.rollback()
            flash('Произошла ошибка при оформлении заказа', 'error')
            return redirect(url_for('site.cart'))

    return render_template('checkout.html')

@bp.route('/generate_sticker', methods=['GET', 'POST'])
@login_required
def generate_sticker_route():
    if request.method == 'POST':
        description = str(request.form.get('description'))
        if not description:
            flash('Введите описание для генерации наклейки', 'error')
            return redirect(url_for('site.generate_sticker_route'))

        # Генерация наклейки
        image_path = generate_sticker(description)
        if not image_path:
            flash('Ошибка при генерации наклейки', 'error')
            return redirect(url_for('site.generate_sticker_route'))
        print(image_path)
        img = '/'.join(image_path.split('/')[-2:])
        print(img)
        # Сохранение наклейки в базу данных
        new_sticker = Product(
            name=description,
            price=random.randint(150, 200),
            img = img,
            category = 'AI'
        )
        db.session.add(new_sticker)
        db.session.commit()

        flash('Наклейка успешно сгенерирована!', 'success')
        return render_template('sticker_preview.html', sticker=new_sticker)

    return render_template('generate_sticker.html')


@bp.route('/upload_sticker', methods=['GET', 'POST'])
@login_required
def upload_sticker_route():
    if request.method == 'POST':
        # Проверяем, есть ли файл в запросе
        if 'file' not in request.files:
            flash('Файл не выбран', 'error')
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash('Файл не выбран', 'error')
            return redirect(request.url)

        if file and allowed_file(file.filename): #  Проверка расширения
            upload_folder = 'app/static/imgs'

            #Проверка на существование папки
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)

            # Получаем оригинальное имя файла без расширения
            original_name, _ = os.path.splitext(secure_filename(file.filename))
            print(original_name, _)
            # Формируем новое имя файла с расширением .gif
            filename = f"{original_name}.gif"

            file_path = os.path.join(upload_folder, filename)

            file.save(file_path)

            new_sticker = Product(
                name=original_name,
                price=random.randint(150, 200),
                img=f'imgs/{filename}',
                category='Пользовательские стикеры',
            )

            db.session.add(new_sticker)
            db.session.commit()

            flash('Изображение успешно загружено!', 'success')
            return render_template('sticker_preview.html', sticker=new_sticker)

    return render_template('upload_sticker.html')
