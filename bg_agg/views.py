from flask import request, redirect, url_for, render_template, flash
from . import app

@app.route("/")
def default():
    return render_template("product.html")

@app.route("/form")
def form():
    return render_template("review_form.html")