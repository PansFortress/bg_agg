import os

class DevelopmentConfig(object):
    DATABASE_URI = "postgresql:///bg_agg"
    DEBUG = True
    SECRET_KEY = os.environ.get("SECRET_KEY", os.urandom(12))

class TestingConfig(object):
    DATABASE_URI = "postgresql:///bg_agg_test"
    DEBUG = True

class HerokuDevConfig(object):
    DATABASE_URI = "postgres://unszlllddfwith:cfd28d506d106f8f4986e75fa6ade194defe8cf17dd307e367a0fc7f739e60d9@ec2-174-129-37-15.compute-1.amazonaws.com:5432/dfuusin4kespkh"
    SECRET_KEY = os.environ.get("SECRET_KEY", os.urandom(12))