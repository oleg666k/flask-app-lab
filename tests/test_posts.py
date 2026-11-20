import unittest

from datetime import datetime

from app import create_app, db
from app.posts.models import Post


class PostTestCase(unittest.TestCase):

    def setUp(self):

        # Створити тестовий застосунок
        self.app = create_app("testing")

        self.client = self.app.test_client()

        # Створення таблиці в тестовій SQLite
        with self.app.app_context():
            db.create_all()

    def tearDown(self):

        # Очищаємо тестову базу
        with self.app.app_context():

            db.session.remove()
            db.drop_all()

    # Дані для заповнення форми
    def post_data(self):

        return {
            "title": "Test Post",
            "content": "This is a test post.",
            "category": "tech",
            "publish_date": "2026-11-20T12:00",
            "enabled": "y"
        }

    # Допоміжний метод створення поста
    def create_test_post(
        self,
        title="Test Post",
        is_active=True
    ):

        with self.app.app_context():

            post = Post(
                title=title,
                content="Test content",
                category="tech",
                posted=datetime(
                    2026, 11, 20, 12, 0
                ),
                is_active=is_active,
                author="Anonymous"
            )

            db.session.add(post)
            db.session.commit()

            return post.id

    # Тест створення поста
    def test_create_post(self):

        response = self.client.post(
            "/post/create",
            data=self.post_data(),
            follow_redirects=True
        )

        self.assertEqual(
            response.status_code,
            200
        )

        with self.app.app_context():

            posts = db.session.scalars(
                db.select(Post)
            ).all()

            self.assertEqual(len(posts), 1)

            self.assertEqual(
                posts[0].title,
                "Test Post"
            )

            self.assertEqual(
                posts[0].author,
                "Anonymous"
            )

    # Тест автора із сесії
    def test_author_from_session(self):

        with self.client.session_transaction() as sess:
            sess["user"] = "admin"

        self.client.post(
            "/post/create",
            data=self.post_data()
        )

        with self.app.app_context():

            post = db.session.scalar(
                db.select(Post)
            )

            self.assertIsNotNone(post)

            self.assertEqual(
                post.author,
                "admin"
            )

    # Тест списку активних постів
    def test_list_posts(self):

        self.create_test_post(
            title="Visible Post",
            is_active=True
        )

        self.create_test_post(
            title="Hidden Post",
            is_active=False
        )

        response = self.client.get("/post")

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertIn(
            b"Visible Post",
            response.data
        )

        self.assertNotIn(
            b"Hidden Post",
            response.data
        )

    # Тест перегляду одного поста
    def test_view_post_detail(self):

        post_id = self.create_test_post()

        response = self.client.get(
            f"/post/{post_id}"
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertIn(
            b"Test Post",
            response.data
        )

    # Тест редагування
    def test_update_post(self):

        post_id = self.create_test_post()

        data = self.post_data()

        data["title"] = "Updated Post"
        data["content"] = "Updated content"

        response = self.client.post(
            f"/post/{post_id}/update",
            data=data,
            follow_redirects=True
        )

        self.assertEqual(
            response.status_code,
            200
        )

        with self.app.app_context():

            post = db.session.get(
                Post,
                post_id
            )

            self.assertEqual(
                post.title,
                "Updated Post"
            )

            self.assertEqual(
                post.content,
                "Updated content"
            )

    # Тест видалення
    def test_delete_post(self):

        post_id = self.create_test_post()

        # Перевірка підтвердження
        response = self.client.get(
            f"/post/{post_id}/delete"
        )

        self.assertEqual(
            response.status_code,
            200
        )

        # Видалення POST запитом
        response = self.client.post(
            f"/post/{post_id}/delete",
            follow_redirects=True
        )

        self.assertEqual(
            response.status_code,
            200
        )

        with self.app.app_context():

            post = db.session.get(
                Post,
                post_id
            )

            self.assertIsNone(post)

    # Тест помилки 404
    def test_404_not_found(self):

        response = self.client.get(
            "/post/999"
        )

        self.assertEqual(
            response.status_code,
            404
        )

    # Тест некоректного введення
    def test_invalid_post(self):

        data = self.post_data()

        data["title"] = ""
        data["content"] = ""

        response = self.client.post(
            "/post/create",
            data=data
        )

        self.assertEqual(
            response.status_code,
            200
        )

        with self.app.app_context():

            posts = db.session.scalars(
                db.select(Post)
            ).all()

            self.assertEqual(
                len(posts),
                0
            )


if __name__ == "__main__":
    unittest.main()