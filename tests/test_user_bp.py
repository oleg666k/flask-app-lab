import unittest

from app import create_app


class FlaskAppTestCase(unittest.TestCase):

    def setUp(self):

        # Створюємо застосунок для тестування
        self.app = create_app("testing")

        self.client = self.app.test_client()

    # Перевірка сторінки привітання
    def test_greetings_page(self):

        response = self.client.get(
            "/hi/John?age=30"
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertIn(
            b"JOHN",
            response.data
        )

        self.assertIn(
            b"30",
            response.data
        )

    # Перевірка сторінки адміністратора
    def test_admin_page(self):

        response = self.client.get(
            "/admin",
            follow_redirects=True
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertIn(
            b"ADMINISTRATOR",
            response.data
        )

        self.assertIn(
            b"45",
            response.data
        )


if __name__ == "__main__":
    unittest.main()