from app import db, app 

#todo-filter based on rating, price
class Service(db.Model):
    __tablename__ = "service"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    time_required_in_hours = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(100), nullable=False)
    about = db.Column(db.String(5000), nullable=False)
    banner = db.Column(db.String(200), nullable=False)
    provider = db.Column(db.Integer, db.ForeignKey("proffessional.id"), nullable=False)

class Customer(db.Model):
    __tablename__ = "customer"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password_hash = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    profile_picture = db.Column(db.String(200), nullable=True)
    address = db.Column(db.String(300), nullable=False)

class Proffessional(db.Model):
    __tablename__ = "proffessional"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password_hash = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    profile_picture = db.Column(db.String(200), nullable=True)

class Request(db.Model):
    __tablename__ = "request"
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey("service.id"))
    customer_id = db.Column(db.Integer, db.ForeignKey("customer.id"))
    proffessional_id = db.Column(db.Integer, db.ForeignKey("proffessional.id"))
    date_of_request = db.Column(db.Date, nullable=False)
    date_of_completion = db.Column(db.Date, nullable=True)
    service_status = db.Column(db.Enum("completed", "cancelled", "inprogress", "assigned", "closed", "rejected", "failed"), nullable=False)

with app.app_context():
    db.create_all()
