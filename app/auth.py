from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import db, Customer, Professional, Admin
from sqlalchemy.exc import SQLAlchemyError
import re

auth = Blueprint('auth', __name__)

# Helper functions for validation
def is_valid_email(email):
    regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$'
    return re.match(regex, str(email)) is not None

def is_valid_password(password):  
    if len(password) < 8:  
        return False  
    if not re.search("[a-z]", password):  
        return False  
    if not re.search("[A-Z]", password):  
        return False  
    if not re.search("[0-9]", password):  
        return False  
    return True  

# Routes
@auth.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        remember = request.form.get('remember') == "on"

        # Validate input
        if not username or not password or not role:
            flash("All fields are required.", "warning")
            return redirect(url_for('auth.login'))

        # Fetch user based on role
        user = None
        if role == "customer":
            user = Customer.query.filter_by(username=username).first()
        elif role == "professional":
            user = Professional.query.filter_by(username=username).first()
        elif role == "admin":
            user = Admin.query.filter_by(username=username).first()

        # Authenticate user
        if user and check_password_hash(user.password_hash, password):
            if user.role != role:
                flash("Invalid role for this account.", "warning")
                return redirect(url_for('auth.login'))
            if getattr(user, 'is_blocked', False):  # Check if the user is blocked
                flash("Your account has been blocked. Please contact support.", "warning")
                return redirect(url_for('auth.login'))

            login_user(user, remember=remember)
            session['role'] = role
            flash("Logged in successfully!", "success")
            return redirect(url_for('customer.home'))
        else:
            flash("Invalid username or password.", "warning")
    return render_template("login.html")


@auth.route('/logout')
def logout():
    try:
        logout_user()
        session.clear()
        flash("Logged out successfully", "success")
    except Exception as e:
        flash("An error occurred during logout: " + str(e), "warning")
    return redirect(url_for('customer.home'))


@auth.route('/signup')
def signup():
    return render_template("signup.html")


@auth.route('/signup-as-customer', methods=["GET", "POST"])
def signup_as_customer():
    if request.method == "POST":
        username = request.form.get('username')
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        password = request.form.get('password')
        email = request.form.get('email')
        address = request.form.get('address')

        if not is_valid_email(email):
            flash("Invalid email address.", "warning")
            return redirect(url_for('auth.signup_as_customer'))
        
        if not is_valid_password(password):
            flash("Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, and one number.", "warning")
            return redirect(url_for('auth.signup_as_customer'))

        if not username or not password or not email or not fname or not lname:
            flash("Please fill all the required fields.", "warning")
            return redirect(url_for('auth.signup_as_customer'))
        
        if Customer.query.filter_by(username=username).first():
            flash("Username already taken.", "warning")
            return redirect(url_for('auth.signup_as_customer'))
        
        if Customer.query.filter_by(email=email).first():
            flash("Email already in use. Please login instead.", "warning")
            return redirect(url_for('auth.signup_as_customer'))
        
        try:
            user = Customer(
                username=username,
                password_hash=generate_password_hash(password),
                email=email,
                fname=fname,
                lname=lname,
                address=address
            )
            db.session.add(user)
            db.session.commit()
            flash("User registered successfully", "success")
            return redirect(url_for('auth.login'))
        except SQLAlchemyError:
            db.session.rollback()
            flash("An error occurred during registration.", "warning")
    return render_template("signup-as-customer.html")


@auth.route('/signup-as-professional', methods=["GET", "POST"])
def signup_as_professional():
    if request.method == "POST":
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        service_type = request.form.get('service_type')  # New
        experience = request.form.get('experience')  # New

        # Basic validation
        if not username or not password or not email or not phone or not service_type or not experience:
            flash("All fields are required.", "warning")
            return redirect(url_for('auth.signup_as_professional'))

        if not is_valid_email(email):
            flash("Invalid email address.", "warning")
            return redirect(url_for('auth.signup_as_professional'))
        
        if not is_valid_password(password):
            flash("Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, and one number.", "warning")
            return redirect(url_for('auth.signup_as_professional'))

        if Professional.query.filter_by(username=username).first():
            flash("Username already taken.", "warning")
            return redirect(url_for('auth.signup_as_professional'))
        
        if Professional.query.filter_by(email=email).first():
            flash("Email already in use. Please login instead.", "warning")
            return redirect(url_for('auth.signup_as_professional'))
        try:
            user = Professional(
                username=username,
                fname=fname,
                lname=lname,
                password_hash=generate_password_hash(password),
                email=email,
                phone=phone,
                address=address,
                service_type=service_type,
                experience=int(experience)  # Ensure integer
            )
            db.session.add(user)
            db.session.commit()
            flash("Professional registered successfully!", "success")
            return redirect(url_for('auth.login'))
        except SQLAlchemyError:
            db.session.rollback()
            flash("An error occurred during registration.", "warning")
    return render_template("signup-as-professional.html")
