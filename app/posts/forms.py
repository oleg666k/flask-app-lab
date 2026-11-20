from datetime import datetime

from flask_wtf import FlaskForm

from wtforms import (
    StringField,
    TextAreaField,
    BooleanField,
    SelectField,
    SubmitField
)

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

    submit = SubmitField(
        "Зберегти пост"
    )


# Форма підтвердження видалення
class DeletePostForm(FlaskForm):

    submit = SubmitField(
        "Видалити пост"
    )