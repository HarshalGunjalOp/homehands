from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

import config
db = SQLAlchemy(app)

import models
import routes
