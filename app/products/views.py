from datetime import datetime
from pathlib import Path
from uuid import uuid4

from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    abort,
    current_app,
    request
)

from tinydb import TinyDB
from werkzeug.utils import secure_filename

from app.products import product_bp
from app.products.forms import ProductForm, DeleteForm


# Шлях до бази даних
def get_database_path():
    path = current_app.config.get("PRODUCT_DB_PATH")

    if path is None:
        path = Path(current_app.root_path).parent / "data" / "products.json"

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    return path


# Папка для фотографій
def get_upload_folder():
    folder = current_app.config.get("PRODUCT_UPLOAD_FOLDER")

    if folder is None:
        folder = Path(current_app.root_path) / "products" / "static" / "uploads"

    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)

    return folder


# Отримання всіх товарів
def get_all_products():
    with TinyDB(get_database_path()) as db:
        return db.table("products").all()


# Пошук товару за ID
def get_product(product_id):
    with TinyDB(get_database_path()) as db:
        return db.table("products").get(doc_id=product_id)


# Збереження фотографії
def save_image(image):
    if not image or not image.filename:
        return None

    original_name = secure_filename(image.filename)
    extension = Path(original_name).suffix.lower()

    filename = f"{uuid4().hex}{extension}"
    path = get_upload_folder() / filename

    image.save(path)

    return f"uploads/{filename}"


# Видалення фотографії
def remove_image(image_path):
    if not image_path:
        return

    filename = Path(image_path).name
    path = get_upload_folder() / filename

    if path.is_file():
        path.unlink()


# Список товарів
@product_bp.route("/product")
@product_bp.route("/product/")
@product_bp.route("/products/")
def list_products():
    products = get_all_products()

    products = sorted(
        products,
        key=lambda product: product["id"],
        reverse=True
    )

    return render_template(
        "products/products.html",
        products=products
    )


# Сторінка одного товару
@product_bp.route("/product/<int:product_id>")
@product_bp.route("/products/<int:product_id>")
def detail_product(product_id):
    product = get_product(product_id)

    if product is None:
        abort(404)

    return render_template(
        "products/detail_product.html",
        product=product,
        delete_form=DeleteForm()
    )


# Додавання товару
@product_bp.route("/product/add", methods=["GET", "POST"])
def add_product():
    form = ProductForm()

    if form.validate_on_submit():
        image_path = None

        try:
            image_path = save_image(form.image.data)

            product = {
                "name": form.name.data.strip(),
                "content": form.content.data.strip(),
                "price": float(form.price.data),
                "category": form.category.data,
                "quantity": form.quantity.data,
                "image": image_path,
                "created_at": datetime.now().isoformat(timespec="seconds")
            }

            with TinyDB(get_database_path()) as db:
                table = db.table("products")

                product_id = table.insert(product)

                table.update(
                    {"id": product_id},
                    doc_ids=[product_id]
                )

            flash("Товар успішно додано!", "success")

            return redirect(url_for("products.list_products"))

        except OSError:
            if image_path:
                remove_image(image_path)

            current_app.logger.exception("Помилка додавання товару")
            flash("Не вдалося зберегти товар.", "error")

    elif request.method == "POST":
        flash("Перевірте правильність введених даних.", "error")

    return render_template(
        "products/product_form.html",
        form=form,
        title="Додати товар",
        product=None
    )


# Редагування товару
@product_bp.route(
    "/product/<int:product_id>/edit",
    methods=["GET", "POST"]
)
def edit_product(product_id):
    product = get_product(product_id)

    if product is None:
        abort(404)

    form = ProductForm()

    if request.method == "GET":
        form.name.data = product["name"]
        form.content.data = product["content"]
        form.price.data = product["price"]
        form.category.data = product["category"]
        form.quantity.data = product["quantity"]

    if form.validate_on_submit():
        new_image = None

        try:
            if form.image.data and form.image.data.filename:
                new_image = save_image(form.image.data)

            updated_product = {
                "name": form.name.data.strip(),
                "content": form.content.data.strip(),
                "price": float(form.price.data),
                "category": form.category.data,
                "quantity": form.quantity.data,
                "image": new_image if new_image else product.get("image")
            }

            with TinyDB(get_database_path()) as db:
                db.table("products").update(
                    updated_product,
                    doc_ids=[product_id]
                )

            if new_image and product.get("image"):
                remove_image(product["image"])

            flash("Товар успішно оновлено!", "success")

            return redirect(
                url_for("products.detail_product", product_id=product_id)
            )

        except OSError:
            if new_image:
                remove_image(new_image)

            current_app.logger.exception("Помилка редагування товару")
            flash("Не вдалося оновити товар.", "error")

    elif request.method == "POST":
        flash("Перевірте правильність введених даних.", "error")

    return render_template(
        "products/product_form.html",
        form=form,
        title="Редагувати товар",
        product=product
    )


# Видалення товару
@product_bp.route(
    "/product/<int:product_id>/delete",
    methods=["POST"]
)
def delete_product(product_id):
    form = DeleteForm()

    if not form.validate_on_submit():
        abort(400)

    product = get_product(product_id)

    if product is None:
        abort(404)

    with TinyDB(get_database_path()) as db:
        db.table("products").remove(doc_ids=[product_id])

    remove_image(product.get("image"))

    flash("Товар успішно видалено!", "success")

    return redirect(url_for("products.list_products"))
