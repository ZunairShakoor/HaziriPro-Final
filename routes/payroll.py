from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from datetime import datetime
from services.payroll_service import PayrollService
from models.employee import Employee
from models.payroll import Payroll
from utils.permissions import hr_required
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

payroll_bp = Blueprint('payroll', __name__)
payroll_service = PayrollService()

@payroll_bp.route('/')
@login_required
@hr_required
def dashboard():
    today = datetime.now()
    month = request.args.get('month', today.month, type=int)
    year = request.args.get('year', today.year, type=int)
    
    summary = payroll_service.get_payroll_summary(month, year)
    
    return render_template('payroll/dashboard.html',
                         summary=summary,
                         month=month,
                         year=year)

@payroll_bp.route('/calculate', methods=['POST'])
@login_required
@hr_required
def calculate():
    month = int(request.form.get('month'))
    year = int(request.form.get('year'))
    
    results = payroll_service.calculate_all_payrolls(month, year)
    
    success_count = sum(1 for r in results if r['success'])
    
    flash(f'Calculated payroll for {success_count} employees.', 'success')
    return redirect(url_for('payroll.dashboard', month=month, year=year))

@payroll_bp.route('/salary/<employee_id>')
@login_required
def salary(employee_id):
    employee = Employee.query.filter_by(employee_id=employee_id).first()
    
    if not employee:
        flash('Employee not found.', 'danger')
        return redirect(url_for('payroll.dashboard'))
    
    # Check permission
    if current_user.role not in ['admin', 'hr']:
        if not current_user.employee or current_user.employee.employee_id != employee_id:
            flash('Unauthorized access.', 'danger')
            return redirect(url_for('dashboard.index'))
    
    payrolls = payroll_service.get_employee_payroll_history(employee_id)
    
    return render_template('payroll/salary.html',
                         employee=employee,
                         payrolls=payrolls)

@payroll_bp.route('/payslip/<int:payroll_id>')
@login_required
def payslip(payroll_id):
    payroll = Payroll.query.get_or_404(payroll_id)
    
    # Check permission
    if current_user.role not in ['admin', 'hr']:
        if not current_user.employee or current_user.employee.id != payroll.employee_id:
            flash('Unauthorized access.', 'danger')
            return redirect(url_for('dashboard.index'))
    
    return render_template('payroll/payslip.html', payroll=payroll)

@payroll_bp.route('/payslip/<int:payroll_id>/download')
@login_required
def download_payslip(payroll_id):
    payroll = Payroll.query.get_or_404(payroll_id)
    
    # Check permission
    if current_user.role not in ['admin', 'hr']:
        if not current_user.employee or current_user.employee.id != payroll.employee_id:
            flash('Unauthorized access.', 'danger')
            return redirect(url_for('dashboard.index'))
    
    # Create PDF
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # Add content
    p.drawString(100, 750, "PAYSLIP")
    p.drawString(100, 720, f"Employee: {payroll.employee.full_name}")
    p.drawString(100, 700, f"Employee ID: {payroll.employee.employee_id}")
    p.drawString(100, 680, f"Period: {payroll.month}/{payroll.year}")
    p.drawString(100, 650, f"Base Salary: Rs. {payroll.base_salary:,.2f}")
    p.drawString(100, 630, f"Overtime Pay: Rs. {payroll.overtime_pay:,.2f}")
    p.drawString(100, 610, f"Bonuses: Rs. {payroll.bonuses:,.2f}")
    p.drawString(100, 590, f"Gross Salary: Rs. {payroll.gross_salary:,.2f}")
    p.drawString(100, 560, f"Tax: Rs. {payroll.tax:,.2f}")
    p.drawString(100, 540, f"Other Deductions: Rs. {payroll.other_deductions:,.2f}")
    p.drawString(100, 510, f"Net Salary: Rs. {payroll.net_salary:,.2f}")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f'payslip_{payroll.employee.employee_id}_{payroll.month}_{payroll.year}.pdf',
        mimetype='application/pdf'
    )

@payroll_bp.route('/approve/<int:payroll_id>', methods=['POST'])
@login_required
@hr_required
def approve(payroll_id):
    success, message = payroll_service.approve_payroll(payroll_id)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    
    return redirect(request.referrer or url_for('payroll.dashboard'))

@payroll_bp.route('/mark-paid/<int:payroll_id>', methods=['POST'])
@login_required
@hr_required
def mark_paid(payroll_id):
    success, message = payroll_service.mark_paid(payroll_id)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    
    return redirect(request.referrer or url_for('payroll.dashboard'))