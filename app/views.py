
from app import app
from flask import render_template


@app.route("/")
def home():
    return render_template("homepage.html")
@app.route("/contacts")
def contacts():
    return render_template("contacts.html")


@app.route("/resume")
def resume():
    return render_template("resume.html")