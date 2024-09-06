from os import walk
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

        user = Customer.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
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
        password = request.form.get('password')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')

        user = Customer(username=username, password_hash=generate_password_hash(password), email=email, phone=phone, address=address)
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
