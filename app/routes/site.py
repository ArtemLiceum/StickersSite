from flask import render_template, Blueprint
from app.models import Product

bp = Blueprint('site', __name__)


@bp.route('/site')
def main_page():
    return render_template('main_page.html')

@bp.route('/site/stickersPacks')
def stickerPacks():
    products = Product.query.filter(Product.category == 'Стикерпак').all()
    return render_template('stickersPacks.html', products=products)