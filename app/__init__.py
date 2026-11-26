import os

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

from .config import (
    DevelopmentConfig,
    TestingConfig,
    ProductionConfig
)


class Base(DeclarativeBase):
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s"
        }
    )


db = SQLAlchemy(model_class=Base)
migrate = Migrate()

# Хешування паролів
bcrypt = Bcrypt()

login_manager = LoginManager()


def create_app(config_name=None):

    configurations = {
        "development": DevelopmentConfig,
        "testing": TestingConfig,
        "production": ProductionConfig
    }

    if config_name is None:
        config_name = os.getenv("APP_ENV", "development")

    app = Flask(__name__)

    app.config.from_object(
        configurations.get(config_name, DevelopmentConfig)
    )

    app.config["SQLALCHEMY_ECHO"] = False

    # Підключення модулів
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # Налаштування FlaskLogin
    login_manager.login_view = "users.login"
    login_manager.login_message = "Please log in first."
    login_manager.login_message_category = "warning"

    from .views import register_routes
    register_routes(app)

    from .users import user_bp
    from .products import product_bp
    from .posts import post_bp

    # Підключення моделей
    from .posts import models as post_models
    from .products import models as product_models
    from .users import models as user_models

    # Реєстрація Blueprints
    app.register_blueprint(user_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(post_bp)

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("404.html"), 404

    return app