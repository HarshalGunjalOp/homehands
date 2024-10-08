from dotenv import load_dotenv
from os import getenv, path, makedirs
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, session
from flask_login import LoginManager
from eralchemy import render_er


db = SQLAlchemy()


def create_app():
    root_dir = path.abspath(path.join(path.dirname(__file__), '..'))
    new_instance_folder = path.join(root_dir, 'database')
    if not path.exists(new_instance_folder):
        makedirs(new_instance_folder)

    app = Flask(__name__, instance_path=new_instance_folder)

    load_dotenv()
    app.config["SQLALCHEMY_DATABASE_URI"] = getenv("SQLALCHEMY_DATABASE_URI")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = getenv("SQLALCHEMY_TRACK_MODIFICATIONS")
    app.config["SECRET_KEY"] = getenv("SECRET_KEY")
    app.config["REMEMBER_COOKIE_DURATION"] = timedelta(days=31)
    db.init_app(app)

    from .admin import admin
    from .customer import customer
    from .professional import professional
    from .auth import auth

    app.register_blueprint(admin, url_prefix="/admin")
    app.register_blueprint(customer, url_prefix="/")
    app.register_blueprint(professional, url_prefix="/professional")
    app.register_blueprint(auth, url_prefix="/auth")

    from .models import Customer, Professional, Admin

    with app.app_context():
        db.create_all()
        render_er(db.Model, 'erd.png')
        print("Database created successfully.")

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        role = session.get('role') 
        
        if role == 'customer':
            return Customer.query.get(int(user_id))
        elif role == 'professional':
            return Professional.query.get(int(user_id))
        elif role == 'admin':
            return Admin.query.get(int(user_id)) 
        else:
            return None 
    
    return app
