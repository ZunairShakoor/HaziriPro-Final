from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from extensions import db
from models.employee import Employee
from models.department import Department
from services.employee_service import EmployeeService
from utils.permissions import hr_required
from datetime import datetime

employees_bp = Blueprint('employees', __name__)
employee_service = EmployeeService()

@employees_bp.route('/')
@login_required
def list():
    # Filters
    department_id = request.args.get('department')
    status = request.args.get('status')
    search = request.args.get('search')
    page = request.args.get('page', 1, type=int)
    
    query = Employee.query
    
    if department_id:
        query = query.filter_by(department_id=department_id)
    if status:
        query = query.filter_by(status=status)
    if search:
        query = query.filter(
            db.or_(
                Employee.employee_id.like(f'%{search}%'),
                Employee.first_name.like(f'%{search}%'),
                Employee.last_name.like(f'%{search}%')
            )
        )

    pagination = query.order_by(Employee.first_name).paginate(page=page, per_page=20, error_out=False)
    employees = pagination.items
    departments = Department.query.all()
    
    return render_template('employees/list.html',
                         employees=employees,
                         departments=departments,
                         pagination=pagination)

@employees_bp.route('/add', methods=['GET', 'POST'])
@login_required
@hr_required
def add():
    if request.method == 'POST':
        data = {
            'username': request.form.get('username'),
            'email': request.form.get('email'),
            'password': request.form.get('password', 'password123'),
            'first_name': request.form.get('first_name'),
            'last_name': request.form.get('last_name'),
            'date_of_birth': datetime.strptime(request.form.get('date_of_birth'), '%Y-%m-%d').date() if request.form.get('date_of_birth') else None,
            'gender': request.form.get('gender'),
            'phone': request.form.get('phone'),
            'address': request.form.get('address'),
            'department_id': request.form.get('department_id'),
            'position': request.form.get('position'),
            'hire_date': datetime.strptime(request.form.get('hire_date'), '%Y-%m-%d').date() if request.form.get('hire_date') else datetime.now().date(),
            'employment_type': request.form.get('employment_type'),
            'base_salary': float(request.form.get('base_salary') or 0),
            'hourly_rate': float(request.form.get('hourly_rate') or 0),
            'role': request.form.get('role', 'employee')
        }
        
        photo = request.files.get('photo')
        
        success, employee, message = employee_service.create_employee(data, photo)
        
        if success:
            flash(message, 'success')
            return redirect(url_for('employees.profile', employee_id=employee.employee_id))
        else:
            flash(message, 'danger')
    
    departments = Department.query.all()
    return render_template('employees/add.html', departments=departments)

@employees_bp.route('/<employee_id>')
@login_required
def profile(employee_id):
    employee = employee_service.get_employee_by_id(employee_id)
    if not employee:
        flash('Employee not found.', 'danger')
        return redirect(url_for('employees.list'))
    
    # Check permission
    if current_user.role not in ['admin', 'hr']:
        if not current_user.employee or current_user.employee.employee_id != employee_id:
            flash('Unauthorized access.', 'danger')
            return redirect(url_for('dashboard.index'))
    
    return render_template('employees/profile.html', employee=employee)

@employees_bp.route('/<employee_id>/edit', methods=['GET', 'POST'])
@login_required
@hr_required
def edit(employee_id):
    employee = employee_service.get_employee_by_id(employee_id)
    if not employee:
        flash('Employee not found.', 'danger')
        return redirect(url_for('employees.list'))
    
    if request.method == 'POST':
        data = {
            'first_name': request.form.get('first_name'),
            'last_name': request.form.get('last_name'),
            'date_of_birth': datetime.strptime(request.form.get('date_of_birth'), '%Y-%m-%d').date() if request.form.get('date_of_birth') else None,
            'gender': request.form.get('gender'),
            'phone': request.form.get('phone'),
            'address': request.form.get('address'),
            'department_id': request.form.get('department_id'),
            'position': request.form.get('position'),
            'employment_type': request.form.get('employment_type'),
            'base_salary': float(request.form.get('base_salary') or 0),
            'hourly_rate': float(request.form.get('hourly_rate') or 0),
            'status': request.form.get('status')
        }
        
        photo = request.files.get('photo')
        
        success, employee, message = employee_service.update_employee(employee_id, data, photo)
        
        if success:
            flash(message, 'success')
            return redirect(url_for('employees.profile', employee_id=employee_id))
        else:
            flash(message, 'danger')
    
    departments = Department.query.all()
    return render_template('employees/edit.html', employee=employee, departments=departments)

@employees_bp.route('/<employee_id>/delete', methods=['POST'])
@login_required
@hr_required
def delete(employee_id):
    success, message = employee_service.delete_employee(employee_id)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('employees.list'))

@employees_bp.route('/<employee_id>/face-registration', methods=['GET', 'POST'])
@login_required
@hr_required
def face_registration(employee_id):
    employee = employee_service.get_employee_by_id(employee_id)
    if not employee:
        flash('Employee not found.', 'danger')
        return redirect(url_for('employees.list'))
    
    if request.method == 'POST':
        photo = request.files.get('photo')
        
        if not photo:
            flash('Please provide a photo.', 'danger')
            return redirect(url_for('employees.face_registration', employee_id=employee_id))
        
        success, message = employee_service.register_face(employee_id, photo)
        
        if success:
            flash(message, 'success')
            return redirect(url_for('employees.profile', employee_id=employee_id))
        else:
            flash(message, 'danger')
    
    return render_template('employees/face_registration.html', employee=employee)