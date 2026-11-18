
import re
from decimal import Decimal

from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileSize
from wtforms import (
    StringField,
    TextAreaField,
    DecimalField,
    IntegerField,
    SelectField,
    FileField,
    SubmitField
)
from wtforms.validators import DataRequired, Length, NumberRange, Optional
from wtforms.validators import ValidationError


class ProductForm(FlaskForm):
    name = StringField(
        "Назва товару",
        validators=[
            DataRequired(message="Введіть назву товару."),
            Length(min=3, message="Мінімум 3 символи.")
        ]
    )

    content = TextAreaField(
        "Опис товару",
        validators=[
            DataRequired(message="Введіть опис товару.")
        ],
        render_kw={"rows": 5, "cols": 40}
    )

    price = DecimalField(
        "Ціна",
        places=2,
        validators=[
            DataRequired(message="Введіть ціну."),
            NumberRange(
                min=Decimal("0.01"),
                message="Ціна повинна бути більшою за нуль."
            )
        ]
    )

    category = SelectField(
        "Категорія",
        choices=[
            ("", "Оберіть категорію"),
            ("Ноутбуки", "Ноутбуки"),
            ("Смартфони", "Смартфони"),
            ("Комп'ютери", "Комп'ютери"),
            ("Аксесуари", "Аксесуари")
        ],
        validators=[DataRequired(message="Оберіть категорію.")]
    )

    quantity = IntegerField(
        "Кількість",
        validators=[
            NumberRange(
                min=0,
                message="Кількість не може бути від'ємною."
            )
        ]
    )

    image = FileField(
        "Фото товару",
        validators=[
            Optional(),
            FileAllowed(
                ["jpg", "jpeg", "png"],
                "Дозволено лише JPG, JPEG або PNG."
            ),
            FileSize(
                max_size=2 * 1024 * 1024,
                message="Максимальний розмір фото — 2 МБ."
            )
        ]
    )

    submit = SubmitField("Зберегти товар")

    def validate_price(self, field):
        # не більше двох знаків після крапки
        raw_value = field.raw_data[0].strip() if field.raw_data else ""

        if not re.fullmatch(r"\d+(\.\d{1,2})?", raw_value):
            raise ValidationError(
                "Введіть ціну з максимум двома знаками після крапки."
            )


class DeleteForm(FlaskForm):
    submit = SubmitField("Видалити товар")
