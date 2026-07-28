from extensions import db
from flask_login import current_user
from models.employee import Employee
from models.user import User
from utils.employee_id import generate_employee_id
from utils.helpers import save_uploaded_file
from ai.face_recognition import FaceRecognitionSystem
from services.notification_service import NotificationService
from services.audit_service import AuditService
from werkzeug.security import generate_password_hash

class EmployeeService:
    def __init__(self):
        self.face_recognition = FaceRecognitionSystem()

    @staticmethod
    def _acting_user_id():
        try:
            return current_user.id if current_user and current_user.is_authenticated else None
        except Exception:
            return None
    
    def create_employee(self, data, photo=None):
        """Create new employee"""
        try:
            # Create user account
            user = User(
                username=data['username'],
                email=data['email'],
                role=data.get('role', 'employee'),
                is_active=True
            )
            user.set_password(data.get('password', 'password123'))
            db.session.add(user)
            db.session.flush()
            
            # Generate employee ID
            employee_id = generate_employee_id()
            
            # Create employee
            employee = Employee(
                employee_id=employee_id,
                user_id=user.id,
                first_name=data['first_name'],
                last_name=data['last_name'],
                date_of_birth=data.get('date_of_birth'),
                gender=data.get('gender'),
                phone=data.get('phone'),
                address=data.get('address'),
                department_id=data.get('department_id'),
                position=data.get('position'),
                hire_date=data.get('hire_date'),
                employment_type=data.get('employment_type', 'full-time'),
                base_salary=data.get('base_salary', 0),
                hourly_rate=data.get('hourly_rate')
            )
            
            # Save photo
            if photo:
                photo_path, _ = save_uploaded_file(photo, 'employees')
                employee.photo_path = photo_path
            
            db.session.add(employee)
            db.session.commit()

            creator_id = self._acting_user_id()

            NotificationService.notify_roles(
                roles=['admin', 'hr'],
                title='New employee added',
                message=f'{employee.full_name} ({employee.employee_id}) joined as {employee.position or "a new employee"}.',
                category='employee',
                icon='user-plus',
                link=f'/employees/{employee.employee_id}',
                exclude_user_id=creator_id,
            )

            AuditService.log(
                user_id=creator_id,
                action='employee.create',
                target_type='Employee',
                target_id=employee.employee_id,
                target_label=employee.full_name,
                details=f'Created with position "{employee.position}", base salary {employee.base_salary}.'
            )

            return True, employee, "Employee created successfully"
        
        except Exception as e:
            db.session.rollback()
            return False, None, f"Error creating employee: {str(e)}"
    
    def update_employee(self, employee_id, data, photo=None):
        """Update employee"""
        try:
            employee = Employee.query.filter_by(employee_id=employee_id).first()
            if not employee:
                return False, None, "Employee not found"

            old_base_salary = employee.base_salary
            old_hourly_rate = employee.hourly_rate
            
            # Update fields
            for key, value in data.items():
                if hasattr(employee, key) and value is not None:
                    setattr(employee, key, value)
            
            # Update photo
            if photo:
                photo_path, _ = save_uploaded_file(photo, 'employees')
                employee.photo_path = photo_path
            
            db.session.commit()

            salary_changed = (
                employee.base_salary != old_base_salary or
                employee.hourly_rate != old_hourly_rate
            )
            if salary_changed:
                AuditService.log(
                    user_id=self._acting_user_id(),
                    action='employee.salary_update',
                    target_type='Employee',
                    target_id=employee.employee_id,
                    target_label=employee.full_name,
                    details=(
                        f'Base salary: {old_base_salary} -> {employee.base_salary}. '
                        f'Hourly rate: {old_hourly_rate} -> {employee.hourly_rate}.'
                    )
                )

            return True, employee, "Employee updated successfully"
        
        except Exception as e:
            db.session.rollback()
            return False, None, f"Error updating employee: {str(e)}"
    
    def delete_employee(self, employee_id):
        """Delete employee"""
        try:
            employee = Employee.query.filter_by(employee_id=employee_id).first()
            if not employee:
                return False, "Employee not found"

            employee_label = employee.full_name
            
            # Delete face encoding
            self.face_recognition.delete_face(employee_id)
            
            # Delete user
            user = employee.user
            db.session.delete(employee)
            db.session.delete(user)
            db.session.commit()

            AuditService.log(
                user_id=self._acting_user_id(),
                action='employee.delete',
                target_type='Employee',
                target_id=employee_id,
                target_label=employee_label,
                details='Employee and linked user account deleted.'
            )
            
            return True, "Employee deleted successfully"
        
        except Exception as e:
            db.session.rollback()
            return False, f"Error deleting employee: {str(e)}"
    
    def register_face(self, employee_id, photo):
        """Register employee face"""
        try:
            employee = Employee.query.filter_by(employee_id=employee_id).first()
            if not employee:
                return False, "Employee not found"
            
            # Save photo — relative_path is for the DB/display (url_for('static', ...)),
            # absolute_path is the real file on disk that face_recognition needs to open.
            relative_path, absolute_path = save_uploaded_file(photo, 'faces')

            if not absolute_path:
                return False, "Invalid photo file. Please upload a PNG, JPG, JPEG, or GIF."
            
            # Register face
            success, message = self.face_recognition.register_face(absolute_path, employee_id)
            
            if success:
                employee.face_encoding_path = relative_path
                db.session.commit()
            
            return success, message
        
        except Exception as e:
            return False, f"Error registering face: {str(e)}"
    
    def get_employee_by_id(self, employee_id):
        """Get employee by ID"""
        return Employee.query.filter_by(employee_id=employee_id).first()
    
    def get_all_employees(self, filters=None):
        """Get all employees with optional filters"""
        query = Employee.query
        
        if filters:
            if 'department_id' in filters:
                query = query.filter_by(department_id=filters['department_id'])
            if 'status' in filters:
                query = query.filter_by(status=filters['status'])
            if 'employment_type' in filters:
                query = query.filter_by(employment_type=filters['employment_type'])
        
        return query.all()
    
    def search_employees(self, search_term):
        """Search employees"""
        return Employee.query.filter(
            db.or_(
                Employee.employee_id.like(f'%{search_term}%'),
                Employee.first_name.like(f'%{search_term}%'),
                Employee.last_name.like(f'%{search_term}%')
            )
        ).all()