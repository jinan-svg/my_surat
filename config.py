# config.py
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:

    SECRET_KEY = "mysurat_secret_key"

    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:@localhost/mysurat"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = "static/uploads"