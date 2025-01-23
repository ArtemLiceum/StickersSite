from flask import session, Blueprint, request, redirect, url_for, render_template, flash
from werkzeug.security import check_password_hash, generate_password_hash
from app import db
from app.models import User

# Импортируйте ваши модели и другие необходимые модули
bp = Blueprint('login', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Находим пользователя по email
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            # Если пользователь найден и пароль верный
            session['user_id'] = user.id  # Создаем сессию
            flash('Вы успешно вошли в систему!', 'success')
            return redirect(url_for('site.main_page'))  # Перенаправляем на главную страницу
        else:
            # Если пользователь не найден или пароль неверный
            flash('Неверный email или пароль', 'error')
            return redirect(url_for('site.login'))

    # Если метод GET, просто отображаем форму
    return render_template('login.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Проверка, что пароли совпадают
        if password != confirm_password:
            flash('Пароли не совпадают', 'error')
            return redirect(url_for('login.register'))

        # Проверка, что пользователь с таким email уже не существует
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Пользователь с таким email уже существует', 'error')
            return redirect(url_for('login.register'))

        # Хеширование пароля
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Создание нового пользователя
        new_user = User(email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Регистрация прошла успешно! Теперь вы можете войти.', 'success')
        return redirect(url_for('login.login'))

    # Если метод GET, просто отображаем форму
    return render_template('register.html')