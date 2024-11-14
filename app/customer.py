from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from .models import db, Request, Service
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_


customer = Blueprint('customer', __name__)


@customer.route('/')
def home():
    return render_template("home.html")


@customer.route('/my-requests')
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


@customer.route('/service/<int:service_id>')
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


@customer.route('/request-service/<int:service_id>')
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


@customer.route('/contact')
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')

        # Basic validation (could expand with regex checks, etc.)
        if not name or not email or not subject or not message:
            flash("All fields are required.", "warning")
            return redirect(url_for('contact'))

        # Here, handle form submission, like sending an email or saving to the database
        flash("Your message has been sent successfully!", "success")
        return redirect(url_for('contact'))
    return render_template("contact.html")


@customer.route('/services')
def services():
    query = request.args.get('query', '')
    pincode = request.args.get('pincode', '')

    if query and pincode:
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


@customer.route('/update-profile', methods=['GET', 'POST'])
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
