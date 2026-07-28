from datetime import datetime
from extensions import db


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)

    # e.g. 'employee.delete', 'employee.salary_update', 'leave.approve', 'payroll.mark_paid'
    action = db.Column(db.String(80), nullable=False, index=True)

    target_type = db.Column(db.String(50))   # e.g. 'Employee', 'Leave', 'Payroll', 'Department'
    target_id = db.Column(db.String(50))      # employee_id string, or numeric PK as string
    target_label = db.Column(db.String(150))  # human-readable, e.g. employee full name

    details = db.Column(db.Text)              # free-text summary of what changed

    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    user = db.relationship('User')

    def __repr__(self):
        return f'<AuditLog {self.action} by user {self.user_id} at {self.created_at}>'
