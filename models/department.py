from datetime import datetime
from extensions import db

class Department(db.Model):
    __tablename__ = 'departments'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.Text)
    manager_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - FIXED
    # Use foreign_keys to specify which foreign key to use for the relationship
    employees = db.relationship(
        'Employee', 
        backref='department', 
        lazy=True,
        foreign_keys='Employee.department_id',
        primaryjoin='Department.id==Employee.department_id'
    )
    
    # Separate relationship for manager
    manager = db.relationship(
        'Employee',
        foreign_keys=[manager_id],
        remote_side='Employee.id',
        post_update=True
    )
    
    def __repr__(self):
        return f'<Department {self.name}>'