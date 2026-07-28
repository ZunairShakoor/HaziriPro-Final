from datetime import datetime
from extensions import db

class Employee(db.Model):
    __tablename__ = 'employees'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    
    # Personal Information
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    
    # Employment Information
    position = db.Column(db.String(100))
    hire_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    employment_type = db.Column(db.String(20))  # full-time, part-time, contract
    status = db.Column(db.String(20), default='active')  # active, inactive, terminated
    
    # Salary Information
    base_salary = db.Column(db.Float, default=0)
    hourly_rate = db.Column(db.Float)
    
    # Documents
    photo_path = db.Column(db.String(255))
    face_encoding_path = db.Column(db.String(255))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - FIXED
    # Don't define department here as it's defined in Department model with backref
    attendances = db.relationship('Attendance', backref='employee', lazy=True, cascade='all, delete-orphan', passive_deletes=True)
    payrolls = db.relationship('Payroll', backref='employee', lazy=True, cascade='all, delete-orphan', passive_deletes=True)
    leaves = db.relationship('Leave', backref='employee', lazy=True, cascade='all, delete-orphan', passive_deletes=True)
    emotions = db.relationship('Emotion', backref='employee', lazy=True, cascade='all, delete-orphan', passive_deletes=True)
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f'<Employee {self.employee_id} - {self.full_name}>'