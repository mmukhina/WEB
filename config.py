import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = 'this-really-needs-to-be-changed'
    SQLALCHEMY_DATABASE_URI = os.environ['postgres://qybkrxdzbfsmnq:4abdee2cf19e5e24290e8b6f813fa91c9fded73e4ac639b3994bd3acf2f77bdb@ec2-3-209-61-239.compute-1.amazonaws.com:5432/dbu1marqhos8n6']


class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
