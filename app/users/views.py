from datetime import datetime, timedelta

from flask import (
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    make_response,
)

from app.users import user_bp


@user_bp.route("/hi/<name>")
def greetings(name):
    age = request.args.get("age", "30")
    return render_template("users/hi.html", name=name, age=age)


@user_bp.route("/admin")
def admin():
    return redirect(
        url_for("users.greetings", name="Administrator", age=45)
    )


@user_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if username == "admin" and password == "123456":
            session["user"] = username
            flash("Ви успішно увійшли!", "success")
            return redirect(url_for("users.profile"))

        flash("Неправильний логін або пароль.", "error")

    return render_template("login.html")


@user_bp.route("/profile")
def profile():
    if "user" not in session:
        flash("Спочатку увійдіть у систему.", "error")
        return redirect(url_for("users.login"))

    cookies = request.cookies
    theme = request.cookies.get("theme", "light")

    return render_template(
        "profile.html",
        username=session["user"],
        cookies=cookies,
        theme=theme,
    )


@user_bp.route("/logout")
def logout():
    session.pop("user", None)
    flash("Ви вийшли із системи.", "success")
    return redirect(url_for("users.login"))


@user_bp.route("/add-cookie", methods=["POST"])
def add_cookie():
    if "user" not in session:
        flash("Спочатку увійдіть у систему.", "error")
        return redirect(url_for("users.login"))

    key = request.form.get("key", "").strip()
    value = request.form.get("value", "").strip()
    days = request.form.get("days", "7").strip()

    if not key or not value:
        flash("Введіть ключ і значення cookie.", "error")
        return redirect(url_for("users.profile"))

    try:
        days = int(days)
        if days < 1:
            raise ValueError
    except ValueError:
        flash("Термін дії має бути цілим числом від 1 дня.", "error")
        return redirect(url_for("users.profile"))

    response = make_response(redirect(url_for("users.profile")))
    response.set_cookie(
        key,
        value,
        expires=datetime.now() + timedelta(days=days),
        httponly=True,
        samesite="Lax",
    )

    flash("Cookie успішно додано.", "success")
    return response


@user_bp.route("/delete-cookie", methods=["POST"])
def delete_cookie():
    if "user" not in session:
        flash("Спочатку увійдіть у систему.", "error")
        return redirect(url_for("users.login"))

    key = request.form.get("key", "").strip()

    if not key:
        flash("Введіть ключ cookie для видалення.", "error")
        return redirect(url_for("users.profile"))

    response = make_response(redirect(url_for("users.profile")))
    response.delete_cookie(key)
    flash("Запит на видалення cookie виконано.", "success")
    return response


@user_bp.route("/delete-all-cookies", methods=["POST"])
def delete_all_cookies():
    if "user" not in session:
        flash("Спочатку увійдіть у систему.", "error")
        return redirect(url_for("users.login"))

    response = make_response(redirect(url_for("users.profile")))

    for key in request.cookies.keys():
        response.delete_cookie(key)

    flash("Надіслано запит на видалення всіх cookie.", "success")
    return response


# Вибір кольорової теми
@user_bp.route("/set-theme", methods=["POST"])
def set_theme():
    if "user" not in session:
        flash("Спочатку увійдіть у систему.", "error")
        return redirect(url_for("users.login"))

    theme = request.form.get("theme", "light")

    if theme not in ("light", "dark"):
        theme = "light"

    response = make_response(redirect(url_for("users.profile")))
    response.set_cookie("theme", theme, max_age=60 * 60 * 24 * 30)

    flash("Кольорову тему змінено.", "success")
    return response
