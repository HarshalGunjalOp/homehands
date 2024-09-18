from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import db, Customer, Professional, Admin
from sqlalchemy.exc import SQLAlchemyError
import re


auth = Blueprint('auth', __name__)


def is_valid_email(email):
    regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$'
    if re.match(regex, email):
        return True
    else:
        return False


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


@auth.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role').lower()
        remember = True if request.form.get('remember')=="on" else False

        if not username or not password:
            flash("Username and password are required.", "warning")
            return redirect(url_for('login'))
    
        try:
            if role=="customer":
                user = Customer.query.filter_by(username=username).first()  
            elif role=="professional":
                user = Professional.query.filter_by(username=username).first()
            elif role=="admin":
                user = Admin.query.filter_by(username=username).first()
            else:
                flash("Invalid role. Please select a role and try again.", "warning")
                return redirect(url_for('login'))
        except SQLAlchemyError:
            flash("User not found. Please check your details and try again.", "warning")
            return redirect(url_for('login'))

        if user and check_password_hash(user.password_hash, password):
            try:
                login_user(user, remember=remember)
                flash("Logged in successfully", "success")
                next_page = request.args.get('next')
                session['role'] = role

                if next_page in [url_for('login'), url_for('signup'), url_for('signup_as_customer'), url_for('signup_as_professional')]:
                    redirect(url_for('home'))

                return redirect(next_page or url_for('home'))
            except Exception as e:
                flash("An error occurred during login: " + str(e), "warning")
        else:
            flash("Invalid username or password", "warning")
    return render_template("login.html")


@auth.route('/logout')
def logout():
    try:
        logout_user()
        session.clear()
        flash("Logged out successfully", "success")
    except Exception as e:
        flash("An error occurred during logout: " + str(e), "warning")
    return redirect(url_for('home'))


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
            return redirect(url_for('register_as_customer'))
        
        if not is_valid_password(password):
            flash("Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, and one number.", "warning")
            return redirect(url_for('register_as_customer'))

        if not username or not password or not email or not fname or not lname:
            flash("Please fill all the required fields.", "warning")
            return redirect(url_for('register_as_customer'))
        
        if Customer.query.filter_by(username=username).first():
            flash("Username already taken.", "warning")
            return redirect(url_for('register_as_customer'))
        
        if Customer.query.filter_by(email=email).first():
            flash("Email already in use. Please login instead.", "warning")
            return redirect(url_for('register_as_customer'))
        

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
            return redirect(url_for('login'))
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

        if not username or not password or not email or not phone:
            flash("Username, password, email, and phone are required.", "warning")
            return redirect(url_for('register_as_professional'))
        
        if not is_valid_email(email):
            flash("Invalid email address.", "warning")
            return redirect(url_for('register_as_customer'))
        
        if not is_valid_password(password):
            flash("Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, and one number.", "warning")
            return redirect(url_for('register_as_customer'))

        if not username or not password or not email or not fname or not lname:
            flash("Please fill all the required fields.", "warning")
            return redirect(url_for('register_as_customer'))
        
        if Customer.query.filter_by(username=username).first():
            flash("Username already taken.", "warning")
            return redirect(url_for('register_as_customer'))
        
        if Customer.query.filter_by(email=email).first():
            flash("Email already in use. Please login instead.", "warning")
            return redirect(url_for('register_as_customer'))

        try:
            user = Professional(
                username=username,
                fname=fname,
                lname=lname,
                password_hash=generate_password_hash(password),
                email=email,
                phone=phone,
                address=address
            )
            db.session.add(user)
            db.session.commit()
            flash("User registered successfully", "success")
            return redirect(url_for('login'))
        except SQLAlchemyError:
            db.session.rollback()
            flash("An error occurred during registration.", "warning")
    return render_template("signup-as-professional.html")
