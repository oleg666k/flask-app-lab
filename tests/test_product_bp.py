import unittest
import tempfile

from pathlib import Path
from io import BytesIO

from app import create_app
from tinydb import TinyDB


class ProductBlueprintTestCase(unittest.TestCase):

    def setUp(self):

        # Тимчасова папка для тестів
        self.temp_dir = tempfile.TemporaryDirectory()

        # Окремий тестовий Flask-застосунок
        self.app = create_app("testing")

        self.app.config.update(
            PRODUCT_DB_PATH=str(
                Path(self.temp_dir.name) / "products.json"
            ),

            PRODUCT_UPLOAD_FOLDER=str(
                Path(self.temp_dir.name) / "uploads"
            )
        )

        self.client = self.app.test_client()

    def tearDown(self):

        # Видаляємо тимчасові файли
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

        with TinyDB(
            self.app.config["PRODUCT_DB_PATH"]
        ) as database:

            return database.table("products").all()

    # Перевірка списку товарів
    def test_products_page(self):

        response = self.client.get("/product")

        self.assertEqual(
            response.status_code,
            200
        )

    # Перевірка додавання
    def test_add_product(self):

        response = self.add_test_product()

        self.assertEqual(
            response.status_code,
            200
        )

        products = self.read_products_from_db()

        self.assertEqual(len(products), 1)

        self.assertEqual(
            products[0]["name"],
            "Laptop"
        )

        self.assertEqual(
            products[0]["quantity"],
            5
        )

        self.assertEqual(
            products[0]["id"],
            1
        )

        self.assertIn(
            "created_at",
            products[0]
        )

    # Перевірка деталей товару
    def test_product_detail(self):

        self.add_test_product()

        response = self.client.get("/product/1")

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertIn(
            b"Laptop",
            response.data
        )

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

        self.assertEqual(
            response.status_code,
            200
        )

        product = self.read_products_from_db()[0]

        self.assertEqual(
            product["name"],
            "Updated Laptop"
        )

        self.assertEqual(
            product["quantity"],
            10
        )

        self.assertEqual(
            product["id"],
            original["id"]
        )

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

        self.assertEqual(
            response.status_code,
            200
        )

        products = self.read_products_from_db()

        self.assertEqual(
            len(products),
            0
        )

    # Перевірка відсутнього товару
    def test_product_not_found(self):

        response = self.client.get("/product/999")

        self.assertEqual(
            response.status_code,
            404
        )

    # Перевірка неправильних даних
    def test_invalid_product(self):

        data = self.product_data()

        data["name"] = "AB"
        data["price"] = "-5"
        data["quantity"] = "-2"

        response = self.client.post(
            "/product/add",
            data=data
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            len(self.read_products_from_db()),
            0
        )

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

        self.assertEqual(
            response.status_code,
            200
        )

        product = self.read_products_from_db()[0]

        self.assertTrue(
            product["image"].endswith(".png")
        )

        image_path = (
            Path(self.app.config["PRODUCT_UPLOAD_FOLDER"])
            / Path(product["image"]).name
        )

        self.assertTrue(image_path.exists())


if __name__ == "__main__":
    unittest.main()