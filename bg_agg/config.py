class DevelopmentConfig(object):
    DATABASE_URI = "postgresql:///bg_agg"
    DEBUG = True

class TestingConfig(object):
    DATABASE_URI = "postgresql:///bg_agg_test"
    DEBUG = True