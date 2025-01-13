from app import db
from app.models import Product
from flask import Blueprint, render_template

bp = Blueprint('data', __name__)

@bp.route('/add_data')
def seed_products():
    products = [
        Product(name="Стикерпак 1", price=238, img="{{ url_for('static', filename='imgs/stickerPacks1.gif') }}", category="Стикерпак"),
        Product(name="Стикерпак 2", price=214, img="{{ url_for('static', filename='imgs/stickerPacks2.gif') }}", category="Стикерпак"),
        Product(name="Стикерпак 3", price=251, img="{{ url_for('static', filename='imgs/stickerPacks3.gif') }}", category="Стикерпак"),
        Product(name="Стикерпак 4", price=350, img="{{ url_for('static', filename='imgs/stickerPacks4.gif') }}", category="Стикерпак"),
        Product(name="Стикерпак 5", price=320, img="{{ url_for('static', filename='imgs/stickerPacks5.gif') }}", category="Стикерпак"),
        Product(name="Стикерпак 6", price=275, img="{{ url_for('static', filename='imgs/stickerPacks6.gif') }}", category="Стикерпак"),
    ]
    try:
        db.session.bulk_save_objects(products)
        db.session.commit()
        print("База данных заполнена карточками.")
    except Exception as e:
        db.session.rollback()
        print('ошибка при заполнении бд')
    finally:
        return render_template('main_page.html')
