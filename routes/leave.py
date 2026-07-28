from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime

from extensions import db
from models.leave import Leave
from models.employee import Employee
from services.notification_service import NotificationService
from services.audit_service import AuditService

leave_bp = Blueprint('leave', __name__)


# ==========================================================
# View Leave Requests
# ==========================================================
@leave_bp.route('/requests')
@login_required
def requests():

    if current_user.role in ['admin', 'hr', 'manager']:
        leaves = Leave.query.order_by(Leave.created_at.desc()).all()
    else:
        employee = Employee.query.filter_by(user_id=current_user.id).first()

        if employee:
            leaves = Leave.query.filter_by(
                employee_id=employee.id
            ).order_by(
                Leave.created_at.desc()
            ).all()
        else:
            leaves = []

    return render_template(
        'leave/requests.html',
        leaves=leaves
    )


# ==========================================================
# Apply Leave
# ==========================================================
@leave_bp.route('/apply', methods=['POST'])
@login_required
def apply():

    employee = Employee.query.filter_by(
        user_id=current_user.id
    ).first()

    if not employee:
        flash('Employee profile not found.', 'danger')
        return redirect(url_for('leave.requests'))

    leave = Leave(
        employee_id=employee.id,
        leave_type=request.form.get('leave_type'),
        start_date=datetime.strptime(
            request.form.get('start_date'),
            '%Y-%m-%d'
        ).date(),
        end_date=datetime.strptime(
            request.form.get('end_date'),
            '%Y-%m-%d'
        ).date(),
        days=(
            datetime.strptime(
                request.form.get('end_date'),
                '%Y-%m-%d'
            ).date()
            -
            datetime.strptime(
                request.form.get('start_date'),
                '%Y-%m-%d'
            ).date()
        ).days + 1,
        reason=request.form.get('reason'),
        status='pending'
    )

    db.session.add(leave)
    db.session.commit()

    NotificationService.notify_roles(
        roles=['admin', 'hr', 'manager'],
        title='New leave request',
        message=f'{employee.full_name} requested {leave.days} day(s) of {leave.leave_type} leave.',
        category='leave',
        icon='calendar-times',
        link=url_for('leave.requests'),
    )

    flash('Leave request submitted successfully.', 'success')

    return redirect(url_for('leave.requests'))


# ==========================================================
# Pending Approvals
# (Reuses leave/requests.html, which already lists every leave
#  — including pending ones — with approve/reject actions for
#  admin/hr/manager. A dedicated approvals.html never existed,
#  which made this route crash with a TemplateNotFound error.)
# ==========================================================
@leave_bp.route('/approvals')
@login_required
def approvals():

    if current_user.role not in ['admin', 'hr', 'manager']:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('dashboard.index'))

    return redirect(url_for('leave.requests'))


# ==========================================================
# Approve Leave
# ==========================================================
@leave_bp.route('/approve/<int:leave_id>', methods=['POST'])
@login_required
def approve(leave_id):

    if current_user.role not in ['admin', 'hr', 'manager']:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('leave.requests'))

    leave = Leave.query.get_or_404(leave_id)

    leave.status = 'approved'
    leave.approved_by = current_user.id
    leave.approved_date = datetime.now()

    db.session.commit()

    NotificationService.notify_user(
        user_id=leave.employee.user_id,
        title='Leave request approved',
        message=f'Your {leave.leave_type} leave from {leave.start_date} to {leave.end_date} was approved.',
        category='leave',
        icon='calendar-check',
        link=url_for('leave.requests'),
    )

    AuditService.log(
        user_id=current_user.id,
        action='leave.approve',
        target_type='Leave',
        target_id=leave.id,
        target_label=leave.employee.full_name,
        details=f'{leave.leave_type} leave, {leave.start_date} to {leave.end_date} ({leave.days} days).'
    )

    flash('Leave request approved successfully.', 'success')

    return redirect(url_for('leave.requests'))


# ==========================================================
# Reject Leave
# ==========================================================
@leave_bp.route('/reject/<int:leave_id>', methods=['POST'])
@login_required
def reject(leave_id):

    if current_user.role not in ['admin', 'hr', 'manager']:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('leave.requests'))

    leave = Leave.query.get_or_404(leave_id)

    leave.status = 'rejected'
    leave.approved_by = current_user.id
    leave.approved_date = datetime.now()
    leave.rejection_reason = request.form.get('reason', '')

    db.session.commit()

    NotificationService.notify_user(
        user_id=leave.employee.user_id,
        title='Leave request rejected',
        message=f'Your {leave.leave_type} leave from {leave.start_date} to {leave.end_date} was rejected.',
        category='leave',
        icon='calendar-times',
        link=url_for('leave.requests'),
    )

    AuditService.log(
        user_id=current_user.id,
        action='leave.reject',
        target_type='Leave',
        target_id=leave.id,
        target_label=leave.employee.full_name,
        details=f'{leave.leave_type} leave, {leave.start_date} to {leave.end_date}. Reason: {leave.rejection_reason or "(none given)"}'
    )

    flash('Leave request rejected successfully.', 'warning')

    return redirect(url_for('leave.requests'))