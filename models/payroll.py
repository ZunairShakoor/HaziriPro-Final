from datetime import datetime
from extensions import db

class Payroll(db.Model):
    __tablename__ = 'payrolls'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    
    # Period
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    
    # Salary Components
    base_salary = db.Column(db.Float, default=0)
    overtime_pay = db.Column(db.Float, default=0)
    bonuses = db.Column(db.Float, default=0)
    allowances = db.Column(db.Float, default=0)
    
    # Deductions
    tax = db.Column(db.Float, default=0)
    insurance = db.Column(db.Float, default=0)
    other_deductions = db.Column(db.Float, default=0)
    
    # Totals
    gross_salary = db.Column(db.Float, default=0)
    net_salary = db.Column(db.Float, default=0)
    
    # Work Details
    work_days = db.Column(db.Integer, default=0)
    overtime_hours = db.Column(db.Float, default=0)
    
    # Status
    status = db.Column(db.String(20), default='pending')  # pending, approved, paid
    paid_date = db.Column(db.Date)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def calculate_totals(self):
        self.gross_salary = (
            self.base_salary + 
            self.overtime_pay + 
            self.bonuses + 
            self.allowances
        )
        
        total_deductions = self.tax + self.insurance + self.other_deductions
        self.net_salary = self.gross_salary - total_deductions
    
    def __repr__(self):
        return f'<Payroll {self.employee_id} - {self.month}/{self.year}>'