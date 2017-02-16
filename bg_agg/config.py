import os

class DevelopmentConfig(object):
    DATABASE_URI = os.environ.get("DATABASE_URL", "postgresql:///bg_agg")
    DEBUG = True
    SECRET_KEY = os.environ.get("SECRET_KEY", os.urandom(12))

class TestingConfig(object):
    DATABASE_URI = "postgresql:///bg_agg_test"
    DEBUG = True