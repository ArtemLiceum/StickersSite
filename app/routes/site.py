from flask import Blueprint, request, redirect, url_for, render_template, flash
from flask_login import login_required, current_user
from app import db
from app.models import Product, Basket, Order
import json

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