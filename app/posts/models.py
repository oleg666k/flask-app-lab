from datetime import datetime

from sqlalchemy import (
    String,
    Text,
    DateTime,
    Enum,
    Boolean,
    true
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from app import db


class Post(db.Model):

    __tablename__ = "posts"

    # Унікальний ID
    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    # Заголовок
    title: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    # Текст публікації
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    # Дата створення
    posted: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    # Категорія
    category: Mapped[str] = mapped_column(
        Enum(
            "news",
            "publication",
            "tech",
            "other",
            name="post_category"
        ),
        nullable=False,
        default="other"
    )

    # Активність публікації
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=true()
    )

    # Автор
    author: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="Anonymous",
        server_default="Anonymous"
    )

    def __repr__(self):
        return f"<Post {self.id}: {self.title}>"