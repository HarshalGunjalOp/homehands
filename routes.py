from flask import render_template, redirect, url_for, request, flash, session
from flask_login import current_user, login_user, logout_user, login_required, LoginManager
from models import db, Customer, Service, Proffessional, Request
from app import app, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import SQLAlchemyError

login_manager = LoginManager(app)

@login_manager.unauthorized_handler
def unauthorized():
    flash("Please log in to view this page.", "warning")
    return redirect(url_for('login'))

@login_manager.user_loader
def loader_user(user_id):
    try:
        return Customer.query.get(user_id)
    except SQLAlchemyError:
        flash("An error occurred while loading user.", "warning")
        return None

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        if not username or not password:
            flash("Username and password are required.", "warning")
            return redirect(url_for('login'))

        try:
            user = Customer.query.filter_by(username=username).first()
        except SQLAlchemyError:
            flash("An error occurred while trying to log in.", "warning")
            return redirect(url_for('login'))

        if user and check_password_hash(user.password_hash, password):
            try:
                login_user(user, remember=remember)
                flash("Logged in successfully", "success")
                next_page = request.args.get('next')

                if next_page in [url_for('login'), url_for('signup'), url_for('signup_as_customer'), url_for('signup_as_proffessional')]:
                    redirect(url_for('home'))

                return redirect(next_page or url_for('home'))
            except Exception as e:
                flash("An error occurred during login: " + str(e), "warning")
        else:
            flash("Invalid username or password", "warning")
    return render_template("login.html")

@app.route('/logout')
def logout():
    try:
        logout_user()
        session.clear()
        flash("Logged out successfully", "success")
    except Exception as e:
        flash("An error occurred during logout: " + str(e), "warning")
    return redirect(url_for('home'))

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/signup')
def signup():
    return render_template("signup.html")

@app.route('/signup-as-customer', methods=["GET", "POST"])
def signup_as_customer():
    if request.method == "POST":
        username = request.form.get('username')
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        password = request.form.get('password')
        email = request.form.get('email')
        address = request.form.get('address')

        if not username or not password or not email or not fname or not lname:
            flash("Please fill all the required fields.", "warning")
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

@app.route('/signup-as-proffessional', methods=["GET", "POST"])
def signup_as_proffessional():
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
            return redirect(url_for('register_as_proffessional'))

        try:
            user = Proffessional(
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
    return render_template("signup-as-proffessional.html")

@app.route('/services')
def services():
    try:
        services = Service.query.all()
    except SQLAlchemyError:
        flash("An error occurred while fetching services.", "warning")
        services = []
    return render_template("services.html", services=services)

@app.route('/service/<int:service_id>')
def service(service_id):
    try:
        service = Service.query.get(service_id)
        if not service:
            flash("Service not found.", "warning")
            return redirect(url_for('services'))
    except SQLAlchemyError:
        flash("An error occurred while fetching the service.", "warning")
        return redirect(url_for('services'))
    return render_template("service.html", service=service)

@app.route('/my-requests')
@login_required
def my_requests():
    try:
        requests = Request.query.filter_by(customer_id=current_user.id).all()

        if not requests:
            flash("You have no service requests at the moment.", "info")
    except SQLAlchemyError as e:
        flash("An error occurred while fetching your requests." + str(e), "warning")
        requests = []
    return render_template("my-requests.html", requests=requests)

@app.route('/request-service/<int:service_id>')
@login_required
def request_service(service_id):
    try:
        service = Service.query.get(service_id)
        if not service:
            flash("Service not found.", "warning")
            return redirect(url_for('services'))

        request = Request(user_id=current_user.id, service_id=service_id)
        db.session.add(request)
        db.session.commit()
        flash("Service requested successfully", "success")
    except SQLAlchemyError:
        db.session.rollback()
        flash("An error occurred while requesting the service.", "warning")
    return redirect(url_for('services'))
