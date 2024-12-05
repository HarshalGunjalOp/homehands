from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from .models import db, Service, Request, Review, Professional
from sqlalchemy.exc import SQLAlchemyError
from .utils import role_required


professional = Blueprint('professional', __name__)


@professional.route('/profile/<int:professional_id>')
def profile(professional_id):
    professional = Professional.query.get(professional_id)

    if not professional:
        flash("Professional not found.", "warning")
        return redirect(url_for('customer.services'))

    reviews = Review.query.filter_by(professional_id=professional_id).all()
    return render_template("professional-profile.html", professional=professional, reviews=reviews)



@professional.route('/my-services')
@login_required
@role_required('professional')
def my_services():
    if not current_user.is_verified:
        flash("Your profile is not verified yet. Please wait for admin approval.", "warning")
        return redirect(url_for('customer.home'))

    try:
        services = Service.query.filter_by(provider_id=current_user.id).all()
        if not services:
            flash("You have not added any services yet.", "info")
    except SQLAlchemyError as e:
        flash("An error occurred while fetching your services." + str(e), "warning")
        services = []
    return render_template("my-services.html", services=services)



@professional.route('/add-service', methods=['GET', 'POST'])
@login_required
@role_required('professional')
def add_service():
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


@professional.route('/update-service/<int:service_id>', methods=['GET', 'POST'])
@login_required
@role_required('professional')
def update_service(service_id):
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


@professional.route('/delete-service/<int:service_id>')
@role_required('professional')
@login_required
def delete_service(service_id):
    try:
        service = Service.query.get(service_id)
        if service:
            db.session.delete(service)
            db.session.commit()
            flash("Service deleted successfully.", "success")
        else:
            flash("Service not found.", "warning")
    except SQLAlchemyError:
        db.session.rollback()
        flash("An error occurred while deleting the service.", "warning")
    
    return redirect(url_for('my_services'))


@professional.route('/update-profile', methods=["GET", "POST"])
@login_required
@role_required('professional')
def update_profile():
    if request.method == "POST":
        current_user.fname = request.form.get('fname')
        current_user.lname = request.form.get('lname')
        current_user.email = request.form.get('email')
        current_user.address = request.form.get('address')
        current_user.phone = request.form.get('phone')
        current_user.service_type = request.form.get('service_type')
        current_user.experience = request.form.get('experience')

        try:
            db.session.commit()
            flash("Profile updated successfully!", "success")
        except SQLAlchemyError:
            db.session.rollback()
            flash("An error occurred while updating the profile.", "warning")

    return render_template('update-profile.html')


@professional.route('/service-requests')
@login_required
@role_required('professional')
def service_requests():
    if not current_user.is_verified:
        flash("Your profile is not verified yet.", "warning")
        return redirect(url_for('customer.home'))

    requests = Request.query.filter_by(professional_id=current_user.id).all()
    return render_template("service-requests.html", requests=requests)


@professional.route('/accept-request/<int:request_id>')
@login_required
@role_required('professional')
def accept_request(request_id):
    request_obj = Request.query.get(request_id)
    if request_obj and request_obj.service_status == "requested":
        request_obj.service_status = "assigned"
        db.session.commit()
        flash("Request accepted successfully!", "success")
    else:
        flash("Request cannot be accepted.", "warning")
    return redirect(url_for('professional.service_requests'))

@professional.route('/close-request/<int:request_id>')
@login_required
@role_required('professional')
def close_request(request_id):
    request_obj = Request.query.get(request_id)
    if request_obj and request_obj.service_status == "inprogress":
        request_obj.service_status = "completed"
        db.session.commit()
        flash("Request closed successfully!", "success")
    else:
        flash("Request cannot be closed.", "warning")
    return redirect(url_for('professional.service_requests'))


@professional.route('/my-reviews')
@login_required
@role_required('professional')
def my_reviews():
    reviews = Review.query.filter_by(professional_id=current_user.id).all()
    return render_template("my-reviews.html", reviews=reviews)
