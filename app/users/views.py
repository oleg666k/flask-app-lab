import re

from datetime import datetime, timedelta

from flask import (
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    make_response,
    current_app,
    abort
)

from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user
)

from sqlalchemy.exc import IntegrityError

from . import user_bp
from .models import User
from .forms import RegistrationForm, LoginForm, ActionForm

from .. import db


@user_bp.app_context_processor
def inject_action_form():
    return {"action_form": ActionForm()}


@user_bp.route("/hi/<name>")
def greetings(name):

    age = request.args.get("age", "30")

    return render_template(
        "users/hi.html",
        name=name,
        age=age
    )


# сторінка адміністратора
@user_bp.route("/admin")
def admin():

    return redirect(
        url_for(
            "users.greetings",
            name="Administrator",
            age=45
        )
    )


@user_bp.route("/register", methods=["GET", "POST"])
def register():

    if current_user.is_authenticated:
        return redirect(url_for("users.account"))

    form = RegistrationForm()

    if form.validate_on_submit():

        # створння користувача
        user = User(
            username=form.username.data,
            email=form.email.data
        )

        # хешуємо пароль
        user.set_password(form.password.data)

        try:
            db.session.add(user)
            db.session.commit()

        except IntegrityError:
            db.session.rollback()
            flash("Username or email already exists.", "error")

            return render_template(
                "register.html",
                form=form
            )

        flash(
            "Account created successfully!",
            "success"
        )

        return redirect(url_for("users.login"))

    return render_template(
        "register.html",
        form=form
    )


# вхід користувача
@user_bp.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for("users.account"))

    form = LoginForm()

    if form.validate_on_submit():

        # пошук користувача 
        user = User.query.filter_by(
            email=form.email.data
        ).first()

        if user and user.check_password(form.password.data):

            if not user.password.startswith("$2"):
                user.set_password(form.password.data)
                db.session.commit()

            login_user(
                user,
                remember=form.remember.data
            )

            session["username"] = user.username

            session.pop("user", None)

            flash(
                "Login successful!",
                "success"
            )

            return redirect(url_for("users.account"))

        flash(
            "Invalid email or password.",
            "error"
        )

    return render_template(
        "login.html",
        form=form
    )


def protected_cookie_names():

    return {
        current_app.config.get(
            "SESSION_COOKIE_NAME", "session"
        ),
        current_app.config.get(
            "REMEMBER_COOKIE_NAME", "remember_token"
        )
    }


# профіль користувача
@user_bp.route("/profile", endpoint="profile")
@user_bp.route("/account")
@login_required
def account():

    cookies = {
        key: value
        for key, value in request.cookies.items()
        if key not in protected_cookie_names()
    }

    theme = request.cookies.get("theme", "light")

    return render_template(
        "account.html",
        username=current_user.username,
        email=current_user.email,
        cookies=cookies,
        theme=theme
    )


# список  користувачів
@user_bp.route("/users")
@login_required
def all_users():

    users = User.query.order_by(User.id).all()

    return render_template(
        "all_users.html",
        users=users,
        count=len(users)
    )


@user_bp.route("/logout", methods=["POST"])
@login_required
def logout():

    if not ActionForm().validate_on_submit():
        abort(400)

    # логаут
    logout_user()

    session.pop("username", None)
    session.pop("user", None)

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(url_for("users.login"))


@user_bp.route("/add-cookie", methods=["POST"])
@login_required
def add_cookie():

    if not ActionForm().validate_on_submit():
        abort(400)

    key = request.form.get("key", "").strip()
    value = request.form.get("value", "").strip()
    days = request.form.get("days", "7")

    if (
        not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", key)
        or not value
        or len(value.encode("utf-8")) > 1000
        or key in protected_cookie_names()
    ):
        flash("Invalid cookie name or value.", "error")
        return redirect(url_for("users.account"))

    try:
        days = int(days)

        if not 1 <= days <= 365:
            raise ValueError

    except ValueError:
        flash("Enter a valid number of days.", "error")
        return redirect(url_for("users.account"))

    response = make_response(
        redirect(url_for("users.account"))
    )

    response.set_cookie(
        key,
        value,
        expires=datetime.now() + timedelta(days=days),
        httponly=True,
        samesite="Lax"
    )

    flash("Cookie added.", "success")

    return response


@user_bp.route("/delete-cookie", methods=["POST"])
@login_required
def delete_cookie():

    if not ActionForm().validate_on_submit():
        abort(400)

    key = request.form.get("key", "").strip()

    if (
        not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", key)
        or key in protected_cookie_names()
    ):
        flash("Invalid cookie name.", "error")
        return redirect(url_for("users.account"))

    response = make_response(
        redirect(url_for("users.account"))
    )

    response.delete_cookie(key)

    flash("Cookie deleted.", "success")

    return response


@user_bp.route("/delete-all-cookies", methods=["POST"])
@login_required
def delete_all_cookies():

    if not ActionForm().validate_on_submit():
        abort(400)

    response = make_response(
        redirect(url_for("users.account"))
    )

    for key in request.cookies.keys():

        if key not in protected_cookie_names():
            response.delete_cookie(key)

    flash("Cookies deleted.", "success")

    return response


@user_bp.route("/set-theme", methods=["POST"])
@login_required
def set_theme():

    if not ActionForm().validate_on_submit():
        abort(400)

    theme = request.form.get("theme", "light")

    if theme not in ("light", "dark"):
        theme = "light"

    response = make_response(
        redirect(url_for("users.account"))
    )

    response.set_cookie(
        "theme",
        theme,
        max_age=60 * 60 * 24 * 30,
        samesite="Lax"
    )

    flash("Theme changed.", "success")

    return response