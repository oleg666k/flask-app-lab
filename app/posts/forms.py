from wtforms import SelectMultipleField
from .models import Tag
from datetime import datetime

from flask_wtf import FlaskForm

from wtforms import (
    StringField,
    TextAreaField,
    BooleanField,
    SelectField,
    SubmitField
)
from .. import db
from ..users.models import User

from wtforms.fields import DateTimeLocalField

from wtforms.validators import (
    DataRequired,
    Length
)


# Форма створення та редагування поста
class PostForm(FlaskForm):

    # Назва поста
    title = StringField(
        "Заголовок",
        validators=[
            DataRequired(
                message="Введіть заголовок."
            ),
            Length(
                max=150,
                message="Максимум 150 символів."
            )
        ]
    )

    # Основний текст
    content = TextAreaField(
        "Текст поста",
        validators=[
            DataRequired(
                message="Введіть текст поста."
            )
        ]
    )

    # Активність поста
    enabled = BooleanField(
        "Активний пост",
        default=True
    )

    # Дата та час публікації
    publish_date = DateTimeLocalField(
        "Дата та час публікації",
        format="%Y-%m-%dT%H:%M",
        default=datetime.now,
        validators=[
            DataRequired(
                message="Вкажіть дату публікації."
            )
        ]
    )

    # Категорія
    category = SelectField(
        "Категорія",
        choices=[
            ("news", "Новини"),
            ("publication", "Публікації"),
            ("tech", "Технології"),
            ("other", "Інше")
        ],
        validators=[
            DataRequired(
                message="Оберіть категорію."
            )
        ]
    )
        # Вибір автора поста
    author_id = SelectField(
        "Автор",
        coerce=int,
        validators=[DataRequired()]
    )
         # Вибір декількох тегів
    tags = SelectMultipleField(
        "Теги",
        coerce=int
    )
    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        # Отримуємо користувачів
        authors = db.session.scalars(
            db.select(User).order_by(User.id)
        ).all()

        self.author_id.choices = [
            (author.id, author.username)
            for author in authors
        ]

        # Отримуємо теги
        tags = db.session.scalars(
            db.select(Tag).order_by(Tag.id)
        ).all()

        self.tags.choices = [
            (tag.id, tag.name)
            for tag in tags
        ]
    submit = SubmitField(
        "Зберегти пост"
    )


# Форма підтвердження видалення
class DeletePostForm(FlaskForm):

    submit = SubmitField(
        "Видалити пост"
    )