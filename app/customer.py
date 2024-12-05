from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from .models import db, Request, Service, Review, Professional
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_
from flask_mail import Message
from os import getenv
from . import mail


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
    if current_user.is_blocked:
        flash("Your account has been blocked. Please contact support.", "warning")
        return redirect(url_for('customer.home'))

    try:
        service = Service.query.get(service_id)
        if not service:
            flash("Service not found.", "warning")
            return redirect(url_for('services'))

        request = Request(customer_id=current_user.id, service_id=service_id)
        db.session.add(request)
        db.session.commit()
        flash("Service requested successfully.", "success")
    except SQLAlchemyError:
        db.session.rollback()
        flash("An error occurred while requesting the service.", "warning")
    return redirect(url_for('services'))


@customer.route('/edit-request/<int:request_id>', methods=["GET", "POST"])
@login_required
def edit_request(request_id):
    request_obj = Request.query.get(request_id)
    if not request_obj or request_obj.customer_id != current_user.id:
        flash("Request not found or unauthorized.", "warning")
        return redirect(url_for('customer.my_requests'))

    if request.method == "POST":
        request_obj.date_of_request = request.form.get('date_of_request')
        request_obj.remarks = request.form.get('remarks')
        db.session.commit()
        flash("Request updated successfully.", "success")
        return redirect(url_for('customer.my_requests'))

    return render_template("edit-request.html", request_obj=request_obj)


@customer.route('/close-request/<int:request_id>')
@login_required
def close_request(request_id):
    request_obj = Request.query.get(request_id)
    if not request_obj or request_obj.customer_id != current_user.id:
        flash("Request not found or unauthorized.", "warning")
        return redirect(url_for('customer.my_requests'))

    if request_obj.service_status == "completed":
        request_obj.service_status = "closed"
        db.session.commit()
        flash("Request closed successfully.", "success")
    else:
        flash("Only completed requests can be closed.", "warning")

    return redirect(url_for('customer.my_requests'))


@customer.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')

        # Basic validation
        if not name or not email or not subject or not message:
            flash("All fields are required.", "warning")
            return redirect(url_for('customer.contact'))

        # Compose the email
        msg = Message(
            subject=f"{subject}",
            sender=email,  # Using the sender's email directly here
            recipients=[getenv("MAIL_USERNAME")],  # Replace with recipient email
            body=f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"
        )
        try:
            mail.send(msg)
            flash("Your message has been sent successfully!", "success")
        except Exception as e:
            flash("An error occurred while sending your message. Please try again later.", "warning")
            print(f"Error: {e}")  # Log the error for debugging

        return redirect(url_for('customer.contact'))


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

    return render_template('services.html', services=services, query=query, pincode=pincode)


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


@customer.route('/add-review/<int:request_id>', methods=["GET", "POST"])
@login_required
def add_review(request_id):
    request_obj = Request.query.get(request_id)

    if not request_obj or request_obj.customer_id != current_user.id:
        flash("Request not found or unauthorized.", "warning")
        return redirect(url_for('customer.my_requests'))

    if request_obj.service_status != "completed":
        flash("You can only review completed requests.", "warning")
        return redirect(url_for('customer.my_requests'))

    if request.method == "POST":
        rating = int(request.form.get('rating'))
        comment = request.form.get('comment', '').strip()

        # Create a new review
        review = Review(
            request_id=request_id,
            professional_id=request_obj.professional_id,
            customer_id=current_user.id,
            rating=rating,
            comment=comment
        )
        db.session.add(review)

        # Update professional's rating
        professional = Professional.query.get(request_obj.professional_id)
        reviews = Review.query.filter_by(professional_id=request_obj.professional_id).all()
        total_rating = sum([r.rating for r in reviews]) + rating
        count = len(reviews) + 1
        professional.rating = total_rating / count

        db.session.commit()
        flash("Review added successfully!", "success")
        return redirect(url_for('customer.my_requests'))

    return render_template("add-review.html", request=request_obj)
