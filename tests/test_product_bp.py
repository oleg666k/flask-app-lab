import unittest
import tempfile

from pathlib import Path
from io import BytesIO

from app import app
from tinydb import TinyDB


class ProductBlueprintTestCase(unittest.TestCase):

    def setUp(self):
        # Створюємо тимчасову папку для тестів
        self.temp_dir = tempfile.TemporaryDirectory()

        self.old_config = {
            key: app.config.get(key)
            for key in [
                "TESTING",
                "WTF_CSRF_ENABLED",
                "PRODUCT_DB_PATH",
                "PRODUCT_UPLOAD_FOLDER"
            ]
        }

        app.config.update(
            TESTING=True,
            WTF_CSRF_ENABLED=False,
            PRODUCT_DB_PATH=str(
                Path(self.temp_dir.name) / "products.json"
            ),
            PRODUCT_UPLOAD_FOLDER=str(
                Path(self.temp_dir.name) / "uploads"
            )
        )

        self.client = app.test_client()

    def tearDown(self):
        # Відновлюємо налаштування після тесту
        for key, value in self.old_config.items():
            if value is None:
                app.config.pop(key, None)
            else:
                app.config[key] = value

        self.temp_dir.cleanup()

    def product_data(self):
        return {
            "name": "Laptop",
            "content": "Ігровий ноутбук для навчання та ігор.",
            "price": "1200.50",
            "category": "Ноутбуки",
            "quantity": "5"
        }

    def add_test_product(self):
        return self.client.post(
            "/product/add",
            data=self.product_data(),
            follow_redirects=True
        )

    def read_products_from_db(self):
        with TinyDB(app.config["PRODUCT_DB_PATH"]) as db:
            return db.table("products").all()

    # Перевірка сторінки товарів
    def test_products_page(self):
        response = self.client.get("/product")

        self.assertEqual(response.status_code, 200)

    # Перевірка додавання
    def test_add_product(self):
        response = self.add_test_product()

        self.assertEqual(response.status_code, 200)

        products = self.read_products_from_db()

        self.assertEqual(len(products), 1)
        self.assertEqual(products[0]["name"], "Laptop")
        self.assertEqual(products[0]["quantity"], 5)
        self.assertEqual(products[0]["id"], 1)
        self.assertIn("created_at", products[0])

    # Перевірка перегляду товару
    def test_product_detail(self):
        self.add_test_product()

        response = self.client.get("/product/1")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Laptop", response.data)

    # Перевірка редагування
    def test_edit_product(self):
        self.add_test_product()

        original = self.read_products_from_db()[0]

        data = self.product_data()
        data["name"] = "Updated Laptop"
        data["price"] = "1500.99"
        data["quantity"] = "10"

        response = self.client.post(
            "/product/1/edit",
            data=data,
            follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)

        product = self.read_products_from_db()[0]

        self.assertEqual(product["name"], "Updated Laptop")
        self.assertEqual(product["quantity"], 10)
        self.assertEqual(product["id"], original["id"])
        self.assertEqual(
            product["created_at"],
            original["created_at"]
        )

    # Перевірка видалення
    def test_delete_product(self):
        self.add_test_product()

        response = self.client.post(
            "/product/1/delete",
            follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)

        products = self.read_products_from_db()

        self.assertEqual(len(products), 0)

    # Перевірка відсутнього товару
    def test_product_not_found(self):
        response = self.client.get("/product/999")

        self.assertEqual(response.status_code, 404)

    # Перевірка неправильного введення
    def test_invalid_product(self):
        data = self.product_data()

        data["name"] = "AB"
        data["price"] = "-5"
        data["quantity"] = "-2"

        response = self.client.post(
            "/product/add",
            data=data
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(self.read_products_from_db()), 0)

    # Перевірка завантаження фотографії
    def test_upload_image(self):
        data = self.product_data()

        data["image"] = (
            BytesIO(b"test image content"),
            "test.png"
        )

        response = self.client.post(
            "/product/add",
            data=data,
            content_type="multipart/form-data",
            follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)

        product = self.read_products_from_db()[0]

        self.assertTrue(product["image"].endswith(".png"))
        self.assertTrue(
            (Path(app.config["PRODUCT_UPLOAD_FOLDER"]) /
             Path(product["image"]).name).exists()
        )


if __name__ == "__main__":
    unittest.main()
