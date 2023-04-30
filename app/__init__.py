from flask import Flask
from app.config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap5
import os


# ENV variables


app = Flask(__name__)
app.config.from_object(Config)
app.config["DEBUG"] = True
os.environ["FOAM_DIR"] = Config.FOAM_DIR
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = "login"
bootstrap = Bootstrap5(app)

from app import routes, models, errors
