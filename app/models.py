from . import db
from flask_login import UserMixin

# TODO:filter based on rating, price
class Service(db.Model):
    __tablename__ = "service"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    time_required_in_hours = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(100), nullable=False)
    about = db.Column(db.String(5000), nullable=False)
    banner = db.Column(db.String(200), nullable=False)
    provider = db.Column(db.Integer, db.ForeignKey("professional.id"), nullable=False)
    rating = db.Column(db.Float, nullable=False, default=0.0)
    pincode = db.Column(db.Integer, nullable=False)

class Customer(UserMixin, db.Model):
    __tablename__ = "customer"
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(50), nullable=False)
    lname = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password_hash = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    profile_picture = db.Column(db.String(150), default='default_user.svg')
    address = db.Column(db.String(300), nullable=True)
    role = db.Column(db.String(20), nullable=False, default='customer')

class Professional(db.Model):
    __tablename__ = "professional"
    id = db.Column(db.Integer, primary_key=True)
    fame = db.Column(db.String(50), nullable=False)
    lname = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password_hash = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    profile_picture = db.Column(db.String(150), default='default_user.svg')
    role = db.Column(db.String(20), nullable=False, default='professional')

class Admin(UserMixin, db.Model):
    __tablename__ = "admin"
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(50), nullable=False)
    lname = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password_hash = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    role = db.Column(db.String(20), nullable=False, default='admin')

class Request(db.Model):
    __tablename__ = "request"
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey("service.id"))
    customer_id = db.Column(db.Integer, db.ForeignKey("customer.id"))
    professional_id = db.Column(db.Integer, db.ForeignKey("professional.id"))
    date_of_request = db.Column(db.Date, nullable=False)
    date_of_completion = db.Column(db.Date, nullable=True)
    service_status = db.Column(db.Enum("completed", "cancelled", "inprogress", "assigned", "closed", "rejected", "failed"), nullable=False)

