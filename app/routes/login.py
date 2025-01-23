from flask import Flask, request, redirect, url_for, session, flash, render_template, blueprints, Blueprint
from werkzeug.security import check_password_hash
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