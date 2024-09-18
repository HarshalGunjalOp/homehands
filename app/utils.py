from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.role != role:
                flash(f"Access denied. {role.capitalize()}s only.", "warning")
                return redirect(url_for('home'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator
