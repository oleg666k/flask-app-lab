
import json
from datetime import datetime
from pathlib import Path

from flask import render_template, redirect, url_for, flash, request
from app import app
from app.forms import ContactForm


@app.route("/")
def home():
    return render_template("homepage.html")


@app.route("/contacts", methods=["GET", "POST"])
@app.route("/contact", methods=["GET", "POST"])
def contacts():
    form = ContactForm()

    if form.validate_on_submit():
        data = {
            "date": datetime.now().isoformat(timespec="seconds"),
            "name": form.name.data,
            "email": form.email.data,
            "phone": form.phone.data,
            "subject": form.subject.data,
            "message": form.message.data
        }

        try:
            log_file = Path(app.root_path).parent / "logs" / "contacts.log"
            log_file.parent.mkdir(parents=True, exist_ok=True)

            with open(log_file, "a", encoding="utf-8") as file:
                file.write(json.dumps(data, ensure_ascii=False) + "\n")

            flash("Повідомлення успішно збережено!", "success")
            return redirect(url_for("contacts"))

        except OSError:
            app.logger.exception("Помилка запису контактної форми")
            flash("Помилка збереження повідомлення.", "error")
            return redirect(url_for("contacts"))

    if request.method == "POST":
        flash("Перевірте правильність заповнення форми.", "error")

    return render_template(
        "contacts.html",
        form=form,
        name="Олег Кузнєцов"
    )


@app.route("/resume")
def resume():
    return render_template("resume.html")
