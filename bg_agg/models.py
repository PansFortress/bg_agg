from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from bg_agg import app
from .database import Base, engine, session

class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True)
    raw_score = Column(String(150))
    score = Column(Float)
    review = Column(String(1500))
    source = Column(String)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    reviewer_id = Column(Integer, ForeignKey('reviewers.id'), nullable=False)

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String(150))
    publisher = Column(String(150))
    release = Column(String(150))
    player_num = Column(String(150))
    image = Column(String)
    reviews = relationship("Review", backref="product")

class Reviewer(Base):
    __tablename__ = "reviewers"
    id = Column(Integer, primary_key=True)
    display_name = Column(String(150))
    critic = Column(Boolean)
    reviews = relationship("Review", backref="reviewer")

Base.metadata.create_all(engine)