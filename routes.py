from flask import render_template, redirect, url_for, request, flash, session
from flask_login import current_user, login_user, logout_user, login_required, LoginManager
from models import db, Customer, Service, Professional, Request
from app import app, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_
import re

login_manager = LoginManager(app)


# /-------------------- AUTHENTICATION ROUTES --------------------/


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


@app.route('/login', methods=["GET", "POST"])
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
                user = Customer.query.filter_by(username=username, role=role).first()  
            elif role=="professional":
                user = Professional.query.filter_by(username=username, role=role).first()
            elif role=="admin":
                user = Customer.query.filter_by(username=username, role=role).first()
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

                if next_page in [url_for('login'), url_for('signup'), url_for('signup_as_customer'), url_for('signup_as_professional')]:
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


@app.route('/signup-as-professional', methods=["GET", "POST"])
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


# /-------------------- CUSTOMER ROUTES --------------------/


@app.route('/')
def home():
    return render_template("home.html")


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


@app.route('/contact')
def contact():
    return render_template("contact.html")


@app.route('/services')
def services():
    query = request.args.get('query', '')
    pincode = request.args.get('pincode', '')

    if query and pincode:
        # Querying the database for services matching the query and pincode
        services = Service.query.filter(
            or_(
                Service.name.ilike(f'%{query}%'),
                Service.description.ilike(f'%{query}%')
            ),
            Service.pincode == pincode
        ).all()
    else:
        services = []

    return render_template('services.html', services=services)


@app.route('/update-profile', methods=['GET', 'POST'])
@login_required
def update_profile():
    if request.method == 'POST':
        current_user.fname = request.form.get('fname')
        current_user.lname = request.form.get('lname')
        current_user.email = request.form.get('email')
        current_user.address = request.form.get('address')
        current_user.phone = request.form.get('phone')

        try:
            db.session.commit()
            flash("Profile updated successfully!", "success")
        except SQLAlchemyError:
            db.session.rollback()
            flash("An error occurred while updating the profile.", "warning")

    return render_template('update_profile.html')


# /-------------------- PROFESSIONAL ROUTES --------------------/


@app.route('/my-services')
@login_required
def my_services():
    if current_user.role != "professional":
        flash("Access denied. Professionals only.", "danger")
        return redirect(url_for('home'))

    try:
        services = Service.query.filter_by(provider_id=current_user.id).all()

        if not services:
            flash("You have not added any services yet.", "info")
    except SQLAlchemyError as e:
        flash("An error occurred while fetching your services." + str(e), "warning")
        services = []
    return render_template("my-services.html", services=services)


@app.route('/add-service', methods=['GET', 'POST'])
@login_required
def add_service():
    if current_user.role != "professional":
        flash("Access denied. Professionals only.", "danger")
        return redirect(url_for('home'))

    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')
        time_required = request.form.get('time_required')
        description = request.form.get('description')
        banner = request.form.get('banner')
        pincode = request.form.get('pincode')

        if not name or not price or not time_required or not description or not pincode:
            flash("All fields are required.", "warning")
            return redirect(url_for('add_service'))
        
        try:
            service = Service(
                name=name,
                price=price,
                time_required_in_hours=time_required,
                description=description,
                banner=banner,
                provider_id=current_user.id,
                pincode=pincode
            )
            db.session.add(service)
            db.session.commit()
            flash("Service added successfully!", "success")
            return redirect(url_for('my_services'))
        except SQLAlchemyError:
            db.session.rollback()
            flash("An error occurred while adding the service.", "warning")

    return render_template('add_service.html')


@app.route('/update-service/<int:service_id>', methods=['GET', 'POST'])
@login_required
def update_service(service_id):
    if current_user.role != "professional":
        flash("Access denied. Professionals only.", "danger")
        return redirect(url_for('home'))

    service = Service.query.get(service_id)
    
    if not service:
        flash("Service not found.", "warning")
        return redirect(url_for('my_services'))

    if request.method == 'POST':
        service.name = request.form.get('name')
        service.price = request.form.get('price')
        service.time_required_in_hours = request.form.get('time_required')
        service.description = request.form.get('description')
        service.banner = request.form.get('banner')
        service.pincode = request.form.get('pincode')

        try:
            db.session.commit()
            flash("Service updated successfully!", "success")
            return redirect(url_for('my_services'))
        except SQLAlchemyError:
            db.session.rollback()
            flash("An error occurred while updating the service.", "warning")

    return render_template('update_service.html', service=service)


@app.route('/delete-service/<int:service_id>')
@login_required
def delete_service(service_id):
    if current_user.role != "professional":
        flash("Access denied. Professionals only.", "danger")
        return redirect(url_for('home'))

    try:
        service = Service.query.get(service_id)
        if service:
            db.session.delete(service)
            db.session.commit()
            flash("Service deleted successfully.", "success")
        else:
            flash("Service not found.", "warning")
    except SQLAlchemyError:
        flash("An error occurred while deleting the service.", "warning")
    
    return redirect(url_for('my_services'))


# /-------------------- ADMIN ROUTES --------------------/


@app.route('/admin-dashboard')
@login_required
def admin_dashboard():
    if current_user.role != "admin":
        flash("Access denied. Admins only.", "danger")
        return redirect(url_for('home'))

    # Fetch all customers, professionals, and services for admin view
    customers = Customer.query.all()
    professionals = Professional.query.all()
    services = Service.query.all()
    
    return render_template('admin_dashboard.html', customers=customers, professionals=professionals, services=services)


@app.route('/admin/approve-professional/<int:professional_id>')
@login_required
def approve_professional(professional_id):
    if current_user.role != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for('home'))

    try:
        professional = Professional.query.get(professional_id)
        if professional:
            professional.is_verified = True  # Assuming a field 'is_verified' exists in the Professional model
            db.session.commit()
            flash("Professional verified successfully.", "success")
        else:
            flash("Professional not found.", "warning")
    except SQLAlchemyError:
        flash("An error occurred while approving the professional.", "warning")
    
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/block-user/<int:user_id>/<string:user_type>')
@login_required
def block_user(user_id, user_type):
    if current_user.role != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for('home'))

    try:
        if user_type == 'customer':
            user = Customer.query.get(user_id)
        else:
            user = Professional.query.get(user_id)

        if user:
            user.is_blocked = not user.is_blocked  # Assuming a 'is_blocked' field in both models
            db.session.commit()
            status = "unblocked" if not user.is_blocked else "blocked"
            flash(f"User successfully {status}.", "success")
        else:
            flash("User not found.", "warning")
    except SQLAlchemyError:
        flash("An error occurred while updating the user.", "warning")
    
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/create-service', methods=['GET', 'POST'])
@login_required
def create_service():
    if current_user.role != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for('home'))

    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')
        time_required = request.form.get('time_required')
        description = request.form.get('description')
        banner = request.form.get('banner')  # Assuming banner is an image URL or path
        provider_id = request.form.get('provider')  # Select from available professionals
        
        if not name or not price or not time_required or not description or not provider_id:
            flash("All fields are required.", "warning")
            return redirect(url_for('create_service'))

        try:
            service = Service(
                name=name,
                price=price,
                time_required_in_hours=time_required,
                description=description,
                banner=banner,
                provider=provider_id  # Foreign key to Professional
            )
            db.session.add(service)
            db.session.commit()
            flash("Service created successfully!", "success")
            return redirect(url_for('admin_dashboard'))
        except SQLAlchemyError:
            db.session.rollback()
            flash("An error occurred while creating the service.", "warning")
    
    professionals = Professional.query.all()
    return render_template('create_service.html', professionals=professionals)


@app.route('/admin/update-service/<int:service_id>', methods=['GET', 'POST'])
@login_required
def update_service(service_id):
    if current_user.role != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for('home'))

    service = Service.query.get(service_id)
    
    if not service:
        flash("Service not found.", "warning")
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        service.name = request.form.get('name')
        service.price = request.form.get('price')
        service.time_required_in_hours = request.form.get('time_required')
        service.description = request.form.get('description')
        service.banner = request.form.get('banner')
        service.provider = request.form.get('provider')

        try:
            db.session.commit()
            flash("Service updated successfully!", "success")
            return redirect(url_for('admin_dashboard'))
        except SQLAlchemyError:
            db.session.rollback()
            flash("An error occurred while updating the service.", "warning")

    professionals = Professional.query.all()
    return render_template('update_service.html', service=service, professionals=professionals)


@app.route('/admin/delete-service/<int:service_id>')
@login_required
def delete_service(service_id):
    if current_user.role != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for('home'))

    try:
        service = Service.query.get(service_id)
        if service:
            db.session.delete(service)
            db.session.commit()
            flash("Service deleted successfully.", "success")
        else:
            flash("Service not found.", "warning")
    except SQLAlchemyError:
        flash("An error occurred while deleting the service.", "warning")
    
    return redirect(url_for('admin_dashboard'))


