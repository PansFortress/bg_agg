import unittest
import os
import shutil
from io import StringIO, BytesIO

import sys; print(list(sys.modules.keys()))
os.environ["CONFIG_PATH"] = "bg_agg.config.TestingConfig"

from bg_agg import app
from bg_agg import models
from bg_agg.database import Base, engine, session

class TestApp(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

        # Set up the tables in the database
        Base.metadata.create_all(engine)

    def tearDown(self):
        session.close()
        Base.metadata.drop_all(engine)

    def test_new_review(self):
        reviewer = models.Reviewer(display_name="test_user", critic=False)
        product = models.Product(name="Settlers of Catan", 
                          publisher="Mayfair Games", 
                          release="1995",
                          player_num="2-4", 
                          image="https://images-na.ssl-images-amazon.com/images/I/615H5ZMhB7L._SX425_.jpg")
        review = models.Review(raw_score="buy", score=5.0, summary="You should buy this game",
                        review="You should definitely buy this game. I would give it a 5.0 out of 5.0.",
                        source="http://randomsource.com",
                        product=product,
                        reviewer=reviewer)
        session.add_all([review])
        session.commit()

        review_check = session.query(models.Review).all()
        self.assertEqual(len(review_check), 1)

        product_check = session.query(models.Product).all()
        self.assertEqual(len(product_check), 1)

        reviewer_check = session.query(models.Reviewer).all()
        self.assertEqual(len(reviewer_check), 1)