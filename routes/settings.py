from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.user import User
from models.employee import Employee
from extensions import db
from config import Config
from utils.validators import validate_password
from services.audit_service import AuditService
from werkzeug.security import generate_password_hash

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.email = request.form.get('email')
        
        # Update password if provided
        new_password = request.form.get('new_password')
        if new_password:
            current_password = request.form.get('current_password')
            if not current_user.check_password(current_password):
                flash('Current password is incorrect.', 'danger')
                return redirect(url_for('settings.profile'))

            password_ok, password_message = validate_password(new_password)
            if not password_ok:
                flash(password_message, 'danger')
                return redirect(url_for('settings.profile'))
            
            current_user.set_password(new_password)
        
        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('settings.profile'))
    
    return render_template('settings/profile.html')

@settings_bp.route('/system')
@login_required
def system():
    if current_user.role != 'admin':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    return render_template('settings/system.html', config=Config)

@settings_bp.route('/audit-log')
@login_required
def audit_log():
    if current_user.role != 'admin':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('dashboard.index'))

    page = request.args.get('page', 1, type=int)
    logs = AuditService.get_paginated(page=page, per_page=25)

    return render_template('settings/audit_log.html', logs=logs)