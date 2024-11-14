from dotenv import load_dotenv
from os import getenv, path, makedirs
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, session
from flask_login import LoginManager
from eralchemy import render_er
from werkzeug.security import generate_password_hash
import subprocess
from flask_mail import Mail

db = SQLAlchemy()
mail = Mail()

def create_default_admin():
    from .models import Admin  # Import the Admin model
    default_username = "admin"  # Choose a username for the default admin
    default_email = "admin@example.com"
    default_password = "securepassword"  # Choose a secure default password

    # Check if the admin user already exists
    existing_admin = Admin.query.filter_by(username=default_username).first()
    if not existing_admin:
        admin = Admin(
            fname="Default",
            lname="Admin",
            username=default_username,
            password_hash=generate_password_hash(default_password),
            email=default_email
        )
        db.session.add(admin)
        db.session.commit()
        print("Default admin created.")
    else:
        print("Admin user already exists.")


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
    app.config.update(
        MAIL_SERVER='localhost',
        MAIL_PORT=1025,
        MAIL_USE_TLS=False,
        MAIL_USE_SSL=False,
        MAIL_USERNAME=None,
        MAIL_PASSWORD=None,
    )
    print("Configured to use local SMTP debugging server.")

    # Start the local SMTP debugging server
    smtpd_command = ['python', '-m', 'aiosmtpd', '-n', '-l', 'localhost:1025']
    subprocess.Popen(smtpd_command)
    print("Local SMTP debugging server started.")

    db.init_app(app)
    mail.init_app(app)

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
        create_default_admin()
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
