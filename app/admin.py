from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from .models import db, Customer, Professional, Service
from sqlalchemy.exc import SQLAlchemyError


admin = Blueprint('admin', __name__)



@admin.route('/admin-dashboard')
@login_required
def admin_dashboard():
    if current_user.role != "admin":
        flash("Access denied. Admins only.", "warning")
        return redirect(url_for('home'))

    # Fetch all customers, professionals, and services for admin view
    customers = Customer.query.all()
    professionals = Professional.query.all()
    services = Service.query.all()
    
    return render_template('admin_dashboard.html', customers=customers, professionals=professionals, services=services)


@admin.route('/admin/approve-professional/<int:professional_id>')
@login_required
def approve_professional(professional_id):
    if current_user.role != "admin":
        flash("Access denied.", "warning")
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


@admin.route('/admin/block-user/<int:user_id>/<string:user_type>')
@login_required
def block_user(user_id, user_type):
    if current_user.role != "admin":
        flash("Access denied.", "warning")
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


@admin.route('/admin/create-service', methods=['GET', 'POST'])
@login_required
def create_service():
    if current_user.role != "admin":
        flash("Access denied.", "warning")
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


@admin.route('/admin/update-service/<int:service_id>', methods=['GET', 'POST'])
@login_required
def update_service(service_id):
    if current_user.role != "admin":
        flash("Access denied.", "warning")
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


@admin.route('/admin/delete-service/<int:service_id>')
@login_required
def delete_service(service_id):
    if current_user.role != "admin":
        flash("Access denied.", "warning")
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


