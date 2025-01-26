from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flasgger import Swagger
import os

db = SQLAlchemy()
migrate = Migrate()

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

    Swagger(app)

    from .routes import dashboard, seed, site, login
    app.register_blueprint(seed.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(site.bp)
    app.register_blueprint(login.bp)

    return app
