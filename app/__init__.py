import os

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase
from app.config import (

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


def create_app(config_name=None):

    configurations = {
        "development": DevelopmentConfig,
        "testing": TestingConfig,
        "production": ProductionConfig
    }

    if config_name is None:
        config_name = os.getenv(
            "APP_ENV",
            "development"
        )

    app = Flask(__name__)

    app.config.from_object(
        configurations.get(
            config_name,
            DevelopmentConfig
        )
    )

    #  розширення
    db.init_app(app)
    migrate.init_app(app, db)

    from app.views import register_routes
    register_routes(app)

    # імпорт Blueprints
    from app.users import user_bp
    from app.products import product_bp
    from app.posts import post_bp

    from app.posts import models

    #  Blueprints
    app.register_blueprint(user_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(post_bp)

    # Обробка помилки 404
    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("404.html"), 404
    from .products import models
    return app