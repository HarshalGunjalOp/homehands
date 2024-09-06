from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)

import config
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

import models
import routes
