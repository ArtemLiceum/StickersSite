from flask import Blueprint, render_template, session, jsonify, request
from app.models import User, Order, Product
from app import db
import json

bp = Blueprint('dashboard', __name__)


@bp.route('/admin')
def dashboard():
    total_users = User.query.count()
    total_orders = Order.query.count()
    total_orders_amount = Order.query.with_entities(db.func.sum(Order.total_amount)).scalar()
    refresh_interval = session.get('refresh_interval', 10)

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


@bp.route('/admin/set_refresh_interval', methods=['POST'])
def set_refresh_interval():
    refresh_interval = request.json.get('refresh_interval')

    valid_intervals = [0, 10, 15, 30, 60]  # в секундах
    if refresh_interval not in valid_intervals:
        return jsonify({'error': 'Invalid interval'}), 400

    session['refresh_interval'] = refresh_interval
    return jsonify({'message': 'Refresh interval updated', 'refresh_interval': refresh_interval})
