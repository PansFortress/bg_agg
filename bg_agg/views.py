from flask import request, redirect, url_for, render_template, flash
from flask_login import login_user
from werkzeug.security  import check_password_hash
from . import app, models
from .database import Base, engine, session

@app.route("/")
def default():
    return render_template("product.html")

@app.route("/game/<int:game_id>/form", methods=["GET"])
def form_get(game_id):
    Product = models.Product
    product = session.query(Product).filter(Product.id==game_id).first()
    if product:
        return render_template("review_form.html", product=product)
    return render_template("404.html"),404

@app.route("/login", methods=["GET"])
def login_get():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login_post():
    username = request.form["username"]
    password = request.form["password"]

    Reviewer = models.Reviewer
    user = session.query(Reviewer).filter(Reviewer.display_name==username).first()
    if not user or not check_password_hash(user.password, password):
        flash("Incorrect username or password", "danger")
        return redirect(url_for("login_get"))

    login_user(user)
    return redirect(request.args.get('next') or url_for("default"))

# TODO: OATH
# TODO: Password reset, email notification, whole infrastructure