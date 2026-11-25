from datetime import datetime

from .. import db

from sqlalchemy import (
    Integer,
    String,
    Float,
    ForeignKey,
    Boolean,
    DateTime,
    func,
    true
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)


class Category(db.Model):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        unique=True
    )

    # Зв'язок один до багатьох
    products: Mapped[list["Product"]] = relationship(
        "Product",
        back_populates="category",
        lazy="select"
    )


class Product(db.Model):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    price: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    # Зовнішній ключ
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id")
    )

    # Зв'язок із категорією
    category: Mapped[Category | None] = relationship(
        "Category",
        back_populates="products"
    )

    # Стан товару
    active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=true()
    )

    # Дата та час створення
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<Product {self.name} - ${self.price}>"