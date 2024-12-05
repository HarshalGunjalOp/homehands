from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user
from .models import Request, db

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.role != role:
                flash(f"Access denied. {role.capitalize()}s only.", "warning")
                return redirect(url_for('customer.home'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def update_request_status(request_id, new_status):
    valid_transitions = {
        "requested": ["assigned", "cancelled"],
        "assigned": ["inprogress", "rejected"],
        "inprogress": ["completed", "failed"],
        "completed": ["closed"],
    }

    request_obj = Request.query.get(request_id)
    if request_obj and new_status in valid_transitions.get(request_obj.service_status, []):
        request_obj.service_status = new_status
        db.session.commit()
        return True
    return False