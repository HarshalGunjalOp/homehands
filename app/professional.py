from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from .models import db, Service
from sqlalchemy.exc import SQLAlchemyError
from .utils import role_required


professional = Blueprint('professional', __name__)


@professional.route('/my-services')
@login_required
@role_required('professional')
def my_services():
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
