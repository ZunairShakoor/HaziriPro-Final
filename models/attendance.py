from datetime import datetime
from extensions import db

class Attendance(db.Model):
    __tablename__ = 'attendances'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    
    # Attendance Details
    date = db.Column(db.Date, nullable=False, index=True)
    check_in = db.Column(db.DateTime)
    check_out = db.Column(db.DateTime)
    
    # Status
    status = db.Column(db.String(20))  # present, absent, late, half-day, leave
    is_late = db.Column(db.Boolean, default=False)
    late_minutes = db.Column(db.Integer, default=0)
    
    # Hours
    work_hours = db.Column(db.Float, default=0)
    overtime_hours = db.Column(db.Float, default=0)
    
    # Location
    check_in_location = db.Column(db.String(255))
    check_out_location = db.Column(db.String(255))
    
    # Notes
    notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def calculate_work_hours(self):
        if self.check_in and self.check_out:
            delta = self.check_out - self.check_in
            self.work_hours = delta.total_seconds() / 3600
    
    def __repr__(self):
        return f'<Attendance {self.employee_id} - {self.date}>'