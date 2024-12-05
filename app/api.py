from flask import Blueprint, jsonify, request
from .models import db, Customer, Professional, Service, Request
from flask_login import login_required

api = Blueprint('api', __name__)

# Get all users
@api.route('/users', methods=['GET'])
@login_required
def get_users():
    users = Customer.query.all()
    professionals = Professional.query.all()
    return jsonify({
        "customers": [{"id": user.id, "name": f"{user.fname} {user.lname}"} for user in users],
        "professionals": [{"id": pro.id, "name": f"{pro.fname} {pro.lname}"} for pro in professionals]
    })

# Get all services
@api.route('/services', methods=['GET'])
def get_services():
    services = Service.query.all()
    return jsonify([{
        "id": service.id,
        "name": service.name,
        "price": service.price,
        "time_required": service.time_required_in_hours,
        "description": service.description,
        "provider_id": service.provider
    } for service in services])

# Create a new service
@api.route('/services', methods=['POST'])
@login_required
def create_service():
    data = request.json
    new_service = Service(
        name=data['name'],
        price=data['price'],
        time_required_in_hours=data['time_required'],
        description=data['description'],
        provider=data['provider_id']
    )
    db.session.add(new_service)
    db.session.commit()
    return jsonify({"message": "Service created successfully!"}), 201

# Get a specific service
@api.route('/services/<int:service_id>', methods=['GET'])
def get_service(service_id):
    service = Service.query.get_or_404(service_id)
    return jsonify({
        "id": service.id,
        "name": service.name,
        "price": service.price,
        "time_required": service.time_required_in_hours,
        "description": service.description,
        "provider_id": service.provider
    })

# Update a service
@api.route('/services/<int:service_id>', methods=['PUT'])
@login_required
def update_service(service_id):
    service = Service.query.get_or_404(service_id)
    data = request.json
    service.name = data.get('name', service.name)
    service.price = data.get('price', service.price)
    service.time_required_in_hours = data.get('time_required', service.time_required_in_hours)
    service.description = data.get('description', service.description)
    db.session.commit()
    return jsonify({"message": "Service updated successfully!"})

# Delete a service
@api.route('/services/<int:service_id>', methods=['DELETE'])
@login_required
def delete_service(service_id):
    service = Service.query.get_or_404(service_id)
    db.session.delete(service)
    db.session.commit()
    return jsonify({"message": "Service deleted successfully!"})
