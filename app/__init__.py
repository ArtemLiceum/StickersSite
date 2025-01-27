from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flasgger import Swagger
import os

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'secret-key')
    app.config['SWAGGER'] = {
        'title': 'Sticker Site API',
        'uiversion': 3
    }
    app.config['SESSION_TYPE'] = 'filesystem'

    db.init_app(app)
    migrate.init_app(app, db)

    login_manager.init_app(app)
    login_manager.login_view = 'site.login'

    Swagger(app)

    from .routes import dashboard, seed, site, login
    app.register_blueprint(seed.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(site.bp)
    app.register_blueprint(login.bp)

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app
