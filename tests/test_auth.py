import unittest

from app import create_app, db
from app.users.models import User


class AuthTestCase(unittest.TestCase):

    def setUp(self):

        self.app = create_app("testing")

        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

    def tearDown(self):

        with self.app.app_context():
            db.session.remove()
            db.drop_all()
            db.engine.dispose()

    def registration_data(self):

        return {
            "username": "testuser",
            "email": "test@example.com",
            "password": "Secret123",
            "confirm_password": "Secret123"
        }

    def register_user(self):

        return self.client.post(
            "/register",
            data=self.registration_data(),
            follow_redirects=True
        )

    def login_user(self):

        return self.client.post(
            "/login",
            data={
                "email": "test@example.com",
                "password": "Secret123"
            },
            follow_redirects=True
        )

    # Завантаження реєстрації
    def test_register_page(self):

        response = self.client.get("/register")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Registration", response.data)

    # Завантаження входу
    def test_login_page(self):

        response = self.client.get("/login")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Login", response.data)

    # Збереження користувача та хешування
    def test_registration(self):

        response = self.register_user()

        self.assertEqual(response.status_code, 200)

        self.assertIn(
            b"Account created successfully!",
            response.data
        )

        with self.app.app_context():

            user = User.query.filter_by(
                email="test@example.com"
            ).first()

            self.assertIsNotNone(user)

            self.assertEqual(
                user.username,
                "testuser"
            )

            self.assertNotEqual(
                user.password,
                "Secret123"
            )

            self.assertTrue(
                user.check_password("Secret123")
            )

            self.assertFalse(
                user.check_password("Wrong123")
            )

    # Повторна реєстрація
    def test_duplicate_registration(self):

        self.register_user()

        response = self.register_user()

        self.assertIn(
            b"Username is already registered.",
            response.data
        )

        self.assertIn(
            b"Email is already registered.",
            response.data
        )

        with self.app.app_context():
            self.assertEqual(User.query.count(), 1)

    #  Успішний вхід
    def test_login(self):

        self.register_user()

        response = self.login_user()

        self.assertEqual(response.status_code, 200)

        self.assertIn(
            b"Login successful!",
            response.data
        )

        with self.client.session_transaction() as session:

            self.assertEqual(
                session["username"],
                "testuser"
            )

            self.assertIn("_user_id", session)

    #  Неправильний пароль
    def test_invalid_login(self):

        self.register_user()

        response = self.client.post(
            "/login",
            data={
                "email": "test@example.com",
                "password": "Wrong123"
            },
            follow_redirects=True
        )

        self.assertIn(
            b"Invalid email or password.",
            response.data
        )

        with self.client.session_transaction() as session:

            self.assertNotIn("_user_id", session)

    #  Вихід із системи
    def test_logout(self):

        self.register_user()
        self.login_user()

        response = self.client.post(
            "/logout",
            follow_redirects=True
        )

        self.assertIn(
            b"You have been logged out.",
            response.data
        )

        with self.client.session_transaction() as session:

            self.assertNotIn("_user_id", session)
            self.assertNotIn("username", session)

    #  Захист профілю
    def test_account_requires_login(self):

        response = self.client.get("/account")

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.location)

    #  Захист списку користувачів
    def test_users_requires_login(self):

        response = self.client.get("/users")

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.location)

    #  Доступ до списку після входу
    def test_users_page(self):

        self.register_user()
        self.login_user()

        response = self.client.get("/users")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"testuser", response.data)
        self.assertIn(b"Total users:", response.data)

    #  Реєстрація після авторизації
    def test_authenticated_register(self):

        self.register_user()
        self.login_user()

        response = self.client.get("/register")

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            response.location.endswith("/account")
        )

    #  Незбіжні паролі
    def test_password_mismatch(self):

        data = self.registration_data()
        data["confirm_password"] = "Another123"

        response = self.client.post(
            "/register",
            data=data
        )

        self.assertIn(
            b"Passwords must match.",
            response.data
        )

        with self.app.app_context():
            self.assertEqual(User.query.count(), 0)


if __name__ == "__main__":
    unittest.main()