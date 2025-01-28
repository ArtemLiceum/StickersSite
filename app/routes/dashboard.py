from flask import Blueprint, render_template, session, jsonify, request
from flask_login import current_user, login_required
from app.models import User, Order, Product
from app import db
import json

bp = Blueprint('dashboard', __name__)


@bp.route('/admin')
def dashboard():
    total_users = User.query.count()
    total_orders = Order.query.count()
    total_orders_amount = Order.query.with_entities(db.func.sum(Order.total_amount)).scalar()

    refresh_interval = 0  # session.get('refresh_interval', 10)

    orders = Order.query.all()
    orders_with_details = []

    for order in orders:
        products = json.loads(order.products)  # Распаковываем JSON из базы
        detailed_products = []

        for product_data in products:
            product = Product.query.get(product_data['id'])
            if product:
                detailed_products.append({
                    'id': product.id,
                    'name': product.name,
                    'img': product.img,
                    'quantity': product_data['quantity'],
                })

        orders_with_details.append({
            'id': order.id,
            'user': order.user,
            'total_amount': order.total_amount,
            'address': order.address,
            'created_at': order.created_at,
            'products': detailed_products,
        })

    return render_template('dashboard.html',
                           orders=orders_with_details,
                           total_users=total_users,
                           total_orders=total_orders,
                           total_orders_amount=total_orders_amount,
                           refresh_interval=refresh_interval
                           )

@bp.route('/admin/update_balance', methods=['POST'])
@login_required
def update_balance():
    user_id = request.json.get('user_id')
    new_balance = request.json.get('balance')

    if not user_id or not new_balance:
        return jsonify({'error': 'Не указан user_id или balance'}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Пользователь не найден'}), 404

    try:
        user.balance = float(new_balance)
        db.session.commit()
        return jsonify({'message': 'Баланс обновлен', 'balance': user.balance})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/admin/set_refresh_interval', methods=['POST'])
def set_refresh_interval():
    refresh_interval = request.json.get('refresh_interval')

    valid_intervals = [0, 10, 15, 30, 60]  # в секундах
    if refresh_interval not in valid_intervals:
        return jsonify({'error': 'Invalid interval'}), 400

    session['refresh_interval'] = refresh_interval
    return jsonify({'message': 'Refresh interval updated', 'refresh_interval': refresh_interval})
