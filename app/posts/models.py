from datetime import datetime

from sqlalchemy import (
    String,
    Text,
    DateTime,
    Enum,
    Boolean,
    ForeignKey,
    true
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from .. import db
from ..users.models import User


# Проміжна таблиця для зв'язку багато до багатьох
post_tags = db.Table(
    "post_tags",

    db.Column(
        "post_id",
        db.Integer,
        db.ForeignKey("posts.id"),
        primary_key=True
    ),

    db.Column(
        "tag_id",
        db.Integer,
        db.ForeignKey("tags.id"),
        primary_key=True
    )
)


class Post(db.Model):

    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)

    title: Mapped[str] = mapped_column(
        String(150), nullable=False
    )

    content: Mapped[str] = mapped_column(
        Text, nullable=False
    )

    posted: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )

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

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=true()
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    # Зв'язок із користувачем
    user: Mapped["User"] = relationship(
        back_populates="posts"
    )

    # Один пост може мати багато тегів
    tags: Mapped[list["Tag"]] = relationship(
        secondary=post_tags,
        back_populates="posts"
    )

    def repr(self):
        return f"<Post {self.id}: {self.title}>"


class Tag(db.Model):

    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False
    )

    # Один тег може належати багатьом постам
    posts: Mapped[list["Post"]] = relationship(
        secondary=post_tags,
        back_populates="tags"
    )

    def repr(self):
        return f"<Tag {self.name}>"