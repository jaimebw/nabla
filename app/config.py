import os
from pathlib import Path


basedir = Path(__file__).resolve().parent


class Config(object):

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
            'sqlite:///'+ str(basedir/'app.db')
    SECRET_KEY = os.environ.get('SECRET_KEY') or "loco-loco"
