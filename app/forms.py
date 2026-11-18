
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Regexp


class ContactForm(FlaskForm):
    name = StringField(
        "Ім'я",
        validators=[
            DataRequired(message="Введіть ім'я."),
            Length(min=4, max=10, message="Ім'я має містити від 4 до 10 символів.")
        ]
    )

    email = StringField(
        "Електронна пошта",
        validators=[
            DataRequired(message="Введіть email."),
            Email(message="Введіть правильну електронну адресу.")
        ]
    )

    phone = StringField(
        "Номер телефону",
        validators=[
            DataRequired(message="Введіть номер телефону."),
            Regexp(
                r"^\+380\d{9}$",
                message="Формат номера: +380XXXXXXXXX"
            )
        ]
    )

    subject = SelectField(
        "Тема повідомлення",
        choices=[
            ("", "Оберіть тему"),
            ("question", "Запитання"),
            ("cooperation", "Співпраця"),
            ("support", "Технічна підтримка"),
            ("other", "Інше")
        ],
        validators=[DataRequired(message="Оберіть тему повідомлення.")]
    )

    message = TextAreaField(
        "Повідомлення",
        validators=[
            DataRequired(message="Введіть повідомлення."),
            Length(max=500, message="Максимум 500 символів.")
        ]
    )

    submit = SubmitField("Надіслати повідомлення")
