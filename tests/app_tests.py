import unittest
import os
import requests

os.environ["CONFIG_PATH"] = "bg_agg.config.TestingConfig"

from bg_agg import app, models
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
        product_2 = models.Product(name="Pandemic",
                                   publisher="Z-Man Games",
                                   release="2007",
                                   player_num="2-5",
                                   image="  http://25.media.tumblr.com/qgIb8tERiqn3b75revfkdxWxo1_500.jpg")
        review_2 = models.Review(raw_score="1", score=1.0, summary="You should not buy this game",
                        review="You should definitely not buy this game. I would give it a 1.0 out of 5.0.",
                        source="http://randomsource.com",
                        product=product_2,
                        reviewer=reviewer)

        session.add_all([review, review_2])
        session.commit()

        review_check = session.query(models.Review).all()
        self.assertEqual(len(review_check), 2)

        product_check = session.query(models.Product).all()
        self.assertEqual(len(product_check), 2)

        reviewer_check = session.query(models.Reviewer).all()
        self.assertEqual(len(reviewer_check), 1)

        # TODO(?) May want to add to this test to make sure the data being put in is the data that
        # comes out and validate that nothing funky or unexpected happen

class TestBGGIntegration(unittest.TestCase):
    def setUp(self):
      pass
    def tearDown(self):
      pass

    def test_bgg_topgames_endpoint(self):
      r = requests.get("https://www.boardgamegeek.com/xmlapi2/hot?type=boardgame")

      self.assertEqual(r.status_code, 200)

    def test_bgg_gameid_endpoint(self):
      r = requests.get("https://www.boardgamegeek.com/xmlapi2/thing?id=1")

      self.assertEqual(r.status_code, 200)
