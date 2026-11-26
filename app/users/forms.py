from flask_wtf import FlaskForm

from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    SubmitField
)

from wtforms.validators import (
    DataRequired,
    Email,
    Length,
    EqualTo,
    Regexp,
    ValidationError
)

from .models import User


class RegistrationForm(FlaskForm):

    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(min=4, max=16),
            Regexp(
                r"^[A-Za-z][A-Za-z0-9_.]*$",
                message="Username must start with a letter."
            )
        ],
        filters=[lambda value: value.strip() if value else value]
    )

    email = StringField(
        "Email",
        validators=[
            DataRequired(),
            Email(),
            Length(max=120)
        ],
        filters=[
            lambda value: value.strip().lower() if value else value
        ]
    )

    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=6, max=72)
        ]
    )

    confirm_password = PasswordField(
        "Confirm password",
        validators=[
            DataRequired(),
            EqualTo(
                "password",
                message="Passwords must match."
            )
        ]
    )

    submit = SubmitField("Register")

    # перевірка унікальності логіна
    def validate_username(self, username):

        user = User.query.filter_by(
            username=username.data
        ).first()

        if user:
            raise ValidationError(
                "Username is already registered."
            )

    # перевірка унікальності email
    def validate_email(self, email):

        user = User.query.filter_by(
            email=email.data
        ).first()

        if user:
            raise ValidationError(
                "Email is already registered."
            )

    # bcrypt пароль до 72 байтів
    def validate_password(self, password):

        if len(password.data.encode("utf-8")) > 72:
            raise ValidationError(
                "Password is too long."
            )


class LoginForm(FlaskForm):

    email = StringField(
        "Email",
        validators=[
            DataRequired(),
            Email(),
            Length(max=120)
        ],
        filters=[
            lambda value: value.strip().lower() if value else value
        ]
    )

    password = PasswordField(
        "Password",
        validators=[DataRequired()]
    )

    remember = BooleanField("Remember me")

    submit = SubmitField("Login")

    def validate_password(self, password):

        if len(password.data.encode("utf-8")) > 72:
            raise ValidationError(
                "Password is too long."
            )


class ActionForm(FlaskForm):
    pass