from functools import wraps
from flask import abort
from flask_login import current_user

def admin_required(f):
    """Require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def hr_required(f):
    """Require HR or admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_hr():
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def manager_required(f):
    """Require manager, HR, or admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_manager():
            abort(403)
        return f(*args, **kwargs)
    return decorated_function