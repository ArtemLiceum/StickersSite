from flask import Blueprint, request, redirect, url_for, render_template, flash
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from app import db
from app.models import User, Order, Product
import json

bp = Blueprint('log', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('site.main_page'))
        else:
            flash('Неверный email или пароль', 'error')
            return redirect(url_for('log.login'))

    return render_template('login.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Пароли не совпадают', 'error')
            return redirect(url_for('log.register'))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Пользователь с таким email уже существует', 'error')
            return redirect(url_for('log.register'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Регистрация прошла успешно! Теперь вы можете войти.', 'success')
        return redirect(url_for('log.login'))

    return render_template('register.html')

@bp.route('/profile')
@login_required
def profile():
    orders = Order.query.filter_by(user_id=current_user.id).all()
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

    return render_template('profile.html',
                           user=current_user,
                           orders_with_details=orders_with_details
                           )

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    # flash('Вы успешно вышли из системы.', 'success')
    return redirect(url_for('site.main_page'))