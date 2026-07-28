from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from models.employee import Employee
from models.attendance import Attendance
from models.payroll import Payroll
from models.department import Department
from models.leave import Leave
from services.attendance_service import AttendanceService
from services.analytics_service import AnalyticsService
from sqlalchemy import func

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    if current_user.role == 'admin':
        return redirect(url_for('dashboard.admin'))
    elif current_user.role == 'hr':
        return redirect(url_for('dashboard.hr'))
    elif current_user.role == 'manager':
        return redirect(url_for('dashboard.manager'))
    else:
        return redirect(url_for('dashboard.employee'))

@dashboard_bp.route('/admin')
@login_required
def admin():
    if current_user.role != 'admin':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    # Statistics
    total_employees = Employee.query.filter_by(status='active').count()
    total_departments = Department.query.count()
    
    # Today's attendance
    attendance_service = AttendanceService()
    attendance_summary = attendance_service.get_daily_attendance_summary()
    
    # Recent employees
    recent_employees = Employee.query.order_by(Employee.created_at.desc()).limit(5).all()
    
    # Pending leaves
    pending_leaves = Leave.query.filter_by(status='pending').count()
    
    # Monthly payroll
    today = datetime.now()
    current_month_payroll = Payroll.query.filter_by(
        month=today.month,
        year=today.year
    ).count()

    # Chart data
    weekly_trend = AnalyticsService.get_weekly_attendance_trend()
    emotion_distribution = AnalyticsService.get_emotion_distribution(days=30)
    department_headcount = AnalyticsService.get_department_headcount()
    payroll_trend = AnalyticsService.get_monthly_payroll_trend(months=6)
    
    return render_template('dashboard/admin.html',
                         total_employees=total_employees,
                         total_departments=total_departments,
                         attendance_summary=attendance_summary,
                         recent_employees=recent_employees,
                         pending_leaves=pending_leaves,
                         current_month_payroll=current_month_payroll,
                         weekly_trend=weekly_trend,
                         emotion_distribution=emotion_distribution,
                         department_headcount=department_headcount,
                         payroll_trend=payroll_trend)

@dashboard_bp.route('/hr')
@login_required
def hr():
    if current_user.role not in ['admin', 'hr']:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    # Statistics
    total_employees = Employee.query.filter_by(status='active').count()
    
    # Today's attendance
    attendance_service = AttendanceService()
    attendance_summary = attendance_service.get_daily_attendance_summary()
    
    # Pending leaves
    pending_leaves = Leave.query.filter_by(status='pending').limit(10).all()
    
    # Recent hires
    recent_hires = Employee.query.order_by(Employee.hire_date.desc()).limit(5).all()

    # Chart data
    weekly_trend = AnalyticsService.get_weekly_attendance_trend()
    emotion_distribution = AnalyticsService.get_emotion_distribution(days=30)
    department_headcount = AnalyticsService.get_department_headcount()
    
    return render_template(
        'dashboard/hr.html',
        total_employees=total_employees,
        attendance_today=attendance_summary.get('present', 0) if isinstance(attendance_summary, dict) else 0,
        payrolls=Payroll.query.count(),
        pending_leaves=len(pending_leaves),
        attendance_summary=attendance_summary,
        recent_hires=recent_hires,
        weekly_trend=weekly_trend,
        emotion_distribution=emotion_distribution,
        department_headcount=department_headcount
    )

@dashboard_bp.route('/manager')
@login_required
def manager():
    if current_user.role not in ['admin', 'hr', 'manager']:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    # Get manager's department
    employee = Employee.query.filter_by(user_id=current_user.id).first()
    if not employee or not employee.department:
        flash('No department assigned.', 'warning')
        return render_template('dashboard/manager.html')
    
    department = employee.department
    
    # Department employees
    dept_employees = Employee.query.filter_by(
        department_id=department.id,
        status='active'
    ).all()
    
    # Today's attendance for department
    today = datetime.now().date()
    dept_attendance = Attendance.query.join(Employee).filter(
        Employee.department_id == department.id,
        Attendance.date == today
    ).all()
    
    # Pending leaves for department
    dept_leaves = Leave.query.join(Employee).filter(
        Employee.department_id == department.id,
        Leave.status == 'pending'
    ).all()
    
    present_today = sum(1 for a in dept_attendance if a.status in ['present','late'])
    total = len(dept_employees)
    absent_today = max(total - present_today, 0)

    return render_template(
        'dashboard/manager.html',
        department=department,
        dept_employees=dept_employees,
        dept_attendance=dept_attendance,
        dept_leaves=dept_leaves,
        total_employees=total,
        present_today=present_today,
        absent_today=absent_today,
        happy_employees=0
    )

@dashboard_bp.route('/employee')
@login_required
def employee():
    # Get employee
    employee = Employee.query.filter_by(user_id=current_user.id).first()
    if not employee:
        flash('Employee profile not found.', 'danger')
        return redirect(url_for('auth.logout'))
    
    # Today's attendance
    today = datetime.now().date()
    today_attendance = Attendance.query.filter_by(
        employee_id=employee.id,
        date=today
    ).first()
    
    # This month's attendance
    start_of_month = today.replace(day=1)
    month_attendances = Attendance.query.filter(
        Attendance.employee_id == employee.id,
        Attendance.date >= start_of_month,
        Attendance.date <= today
    ).all()
    
    present_days = sum(1 for a in month_attendances if a.status in ['present', 'late'])
    total_hours = sum(a.work_hours or 0 for a in month_attendances)
    
    # Recent payrolls
    recent_payrolls = Payroll.query.filter_by(
        employee_id=employee.id
    ).order_by(Payroll.year.desc(), Payroll.month.desc()).limit(3).all()
    
    # Leave balance (simplified)
    used_leaves = Leave.query.filter_by(
        employee_id=employee.id,
        status='approved'
    ).count()
    
    total_leave_allowance = 20  # Annual leave days
    remaining_leaves = total_leave_allowance - used_leaves
    
    return render_template('dashboard/employee.html',
                         employee=employee,
                         today_attendance=today_attendance,
                         present_days=present_days,
                         total_hours=total_hours,
                         recent_payrolls=recent_payrolls,
                         remaining_leaves=remaining_leaves)