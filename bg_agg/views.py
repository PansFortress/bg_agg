from flask import request, redirect, url_for, render_template, flash
from flask_login import login_user, login_required, current_user, logout_user
from werkzeug.security  import check_password_hash
from sqlalchemy import func
from . import app, models
from .database import Base, engine, session

@app.route("/")
def default():
    return render_template("product_mockup.html")

@app.route("/game/<int:game_id>", methods=["GET"])
def game_get(game_id):
    Product = models.Product
    product = session.query(Product).filter(Product.id==game_id).first()

    # TODO Need to investigate how to 1) Use SQLAlchemy to SUM a column up
    # 2) join on Reviewers who are Critics
    Review = models.Review
    Reviewer = models.Reviewer

    critic_reviews = session.query(Review).join(Review.reviewer).\
             filter(Review.product == product).\
             filter(Reviewer.critic == True).\
             values(Reviewer.critic,
                    Reviewer.display_name,
                    Review.raw_score,
                    Review.score,
                    Review.review,
                    Review.source)

    reviews = session.query(Review).join(Review.reviewer).\
             filter(Review.product == product).\
             filter(Reviewer.critic == False).\
             values(Reviewer.critic,
                    Reviewer.display_name,
                    Review.raw_score,
                    Review.score,
                    Review.review,
                    Review.source)

    if product:
        return render_template("product.html", product=product, 
                                critic_reviews=critic_reviews,reviews=reviews)
    return render_template("404.html"),404

@app.route("/game/<int:game_id>/form", methods=["GET"])
@login_required
def form_get(game_id):
    Product = models.Product
    product = session.query(Product).filter(Product.id==game_id).first()
    if product:
        return render_template("review_form.html", product=product)
    return render_template("404.html"),404

@app.route("/game/<int:game_id>/form", methods=["POST"])
@login_required
def form_post(game_id):
    Product = models.Product
    product = session.query(Product).filter(Product.id==game_id).first()
    
    review = models.Review(raw_score=request.form["radioScore"],
                           score=request.form["radioScore"],
                           summary=request.form["inputSummary"],
                           review=request.form["inputReview"],
                           product=product,
                           reviewer=current_user)

    session.add(review)
    session.commit()

    flash("Your review's been submitted. Thanks so much!", "success")

    return(redirect(url_for("get_game", game_id=product.id)))


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
    return redirect(request.args.get('next') or url_for("form_get", game_id=1))

# TODO: OATH
# TODO: Password reset, email notification, whole infrastructure