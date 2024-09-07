from flask import Flask, render_template, redirect, url_for, request, flash 
from flask_login import current_user, login_user, logout_user
from models import db, Customer, Service, Proffessional, Request 

from app import app, login_manager
from werkzeug.security import generate_password_hash, check_password_hash 

@login_manager.user_loader
def loader_user(user_id):
    return Customer.query.get(user_id)

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method=="POST":
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        user = Customer.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            if remember:
                login_user(user, remember=True)
            login_user(user)
            flash("Logged in successfully")
            return redirect(url_for('home'))
        else:
            flash("Invalid username or password")
    return render_template("login.html")

@app.route('/logout')
def logout():
    logout_user()
    flash("Logged out successfully")
    return redirect(url_for('home'))

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/signup')
def register():
    return render_template("signup.html")

@app.route('/signup-as-customer', methods=["GET", "POST"])
def register_as_customer():
    if request.method == "POST":
        username = request.form.get('username')
        name = request.form.get('name')
        password = request.form.get('password')
        email = request.form.get('email')
        address = request.form.get('address')

        user = Customer(username=username, password_hash=generate_password_hash(password), email=email, name=name, address=address)
        db.session.add(user)
        db.session.commit()
        flash("User registered successfully")
        return redirect(url_for('login'))
    return render_template("signup-as-customer.html")

@app.route('/signup-as-proffessional', methods=["GET", "POST"])
def register_as_proffessional():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')

        user = Proffessional(username=username, password_hash=generate_password_hash(password), email=email, phone=phone, address=address)
        db.session.add(user)
        db.session.commit()
        flash("User registered successfully")
        return redirect(url_for('login'))
    return render_template("signup-as-proffessional.html")

@app.route('/services')
def services():
    services = Service.query.all()
    return render_template("services.html", services=services)

@app.route('/service/<int:service_id>')
def service(service_id):
    service = Service.query.get(service_id)
    return render_template("service.html", service=service)

@app.route('/my-requests')
def my_requests():
    requests = Request.query.filter_by(user_id=current_user.id).all()
    return render_template("my-requests.html", requests=requests)

@app.route('/request-service/<int:service_id>')
def request_service(service_id):
    service = Service.query.get(service_id)
    request = Request(user_id=current_user.id, service_id=service_id)
    db.session.add(request)
    db.session.commit()
    flash("Service requested successfully")
    return redirect(url_for('services'))
