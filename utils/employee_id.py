import random
import string
from models.employee import Employee

def generate_employee_id(prefix='EMP'):
    """Generate unique employee ID"""
    while True:
        # Generate random 6-digit number
        number = ''.join(random.choices(string.digits, k=6))
        employee_id = f"{prefix}{number}"
        
        # Check if ID already exists
        if not Employee.query.filter_by(employee_id=employee_id).first():
            return employee_id