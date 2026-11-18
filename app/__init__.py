
import os
from flask import Flask

app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY",
    "lab5-development-secret-key"
)

app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

from app import views

from app.users import user_bp
from app.products import product_bp

app.register_blueprint(user_bp)
app.register_blueprint(product_bp)
