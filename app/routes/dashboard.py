from itertools import product

from flask import Blueprint, render_template, session, jsonify, request
from app.models import User, Basket

bp = Blueprint('dashboard', __name__)


@bp.route('/')
def dashboard():
    total_users = User.query.count()
    refresh_interval = session.get('refresh_interval', 10)
    return render_template('dashboard.html',
                           total_users=total_users,
                           refresh_interval=refresh_interval)

@bp.route('/set_refresh_interval', methods=['POST'])
def set_refresh_interval():
    refresh_interval = request.json.get('refresh_interval')

    valid_intervals = [0, 10, 15, 30, 60]  # в секундах
    if refresh_interval not in valid_intervals:
        return jsonify({'error': 'Invalid interval'}), 400

    session['refresh_interval'] = refresh_interval
    return jsonify({'message': 'Refresh interval updated', 'refresh_interval': refresh_interval})