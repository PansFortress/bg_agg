from flask import request, redirect, url_for, render_template, flash
from . import app, models
from .database import Base, engine, session

@app.route("/")
def default():
    return render_template("product.html")

@app.route("/game/<int:game_id>/form")
def form(game_id):
    Product = models.Product
    product = session.query(Product).filter(Product.id==game_id).first()
    if product:
        return render_template("review_form.html", product=product)
    return render_template("404.html"),404

# TODO: OATH
# TODO: Password reset, email notification, whole infrastructure