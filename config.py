import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

S3_BUCKET = os.environ["S3_BUCKET"]
S3_KEY = os.environ["S3_KEY"]
S3_SECRET = os.environ["S3_SECRET"]
S3_OBJECT_LOCATION = os.environ["S3_OBJECT_LOCATION"]

class Config:
    SECRET_KEY = os.environ['FLASK_SECRET_KEY']
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    UPLOAD_DIRECTORY = os.path.join('app', 'static', 'res', 'uploads') 
    UPLOAD_DIRECTORY_TMP = os.path.join('app', 'static', 'res', 'tmp') 
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    


class TestingConfig(Config):
    TESTING = True
  

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': ProductionConfig

}