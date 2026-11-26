from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from flask_login import UserMixin
from werkzeug.security import check_password_hash

from .. import db, bcrypt, login_manager


class User(db.Model, UserMixin):

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    username: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(120), unique=True, nullable=False
    )

    password: Mapped[str] = mapped_column(
        String(255), nullable=False
    )

    # Зв'язок користувача з постами
    posts: Mapped[list["Post"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )

    # хешування  пароля
    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(
            password
        ).decode("utf-8")

    # перевірка введеного пароля
    def check_password(self, password):

        try:
            if self.password.startswith("$2"):
                return bcrypt.check_password_hash(
                    self.password, password
                )

            if self.password.startswith(
                ("scrypt:", "pbkdf2:")
            ):
                return check_password_hash(
                    self.password, password
                )

        except ValueError:
            return False

        return False

    def __repr__(self):
        return f"<User {self.username}>"


# завантаження користувача за ID
@login_manager.user_loader
def load_user(user_id):

    try:
        return db.session.get(User, int(user_id))

    except (ValueError, TypeError):
        return None