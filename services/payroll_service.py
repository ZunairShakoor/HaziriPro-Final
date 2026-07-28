from datetime import datetime, date
from calendar import monthrange
from flask_login import current_user
from extensions import db
from models.payroll import Payroll
from models.employee import Employee
from models.attendance import Attendance
from config import Config
from services.audit_service import AuditService


def _acting_user_id():
    try:
        return current_user.id if current_user and current_user.is_authenticated else None
    except Exception:
        return None

class PayrollService:
    def calculate_monthly_payroll(self, employee_id, month, year):
        """Calculate payroll for an employee"""
        try:
            employee = Employee.query.filter_by(employee_id=employee_id).first()
            if not employee:
                return False, None, "Employee not found"
            
            # Get attendance for the month
            start_date = date(year, month, 1)
            _, last_day = monthrange(year, month)
            end_date = date(year, month, last_day)
            
            attendances = Attendance.query.filter(
                Attendance.employee_id == employee.id,
                Attendance.date >= start_date,
                Attendance.date <= end_date
            ).all()
            
            # Calculate work days and overtime
            work_days = sum(1 for a in attendances if a.status in ['present', 'late'])
            total_overtime = sum(a.overtime_hours or 0 for a in attendances)
            
            # Calculate salary components
            base_salary = employee.base_salary
            overtime_pay = 0
            
            if employee.hourly_rate:
                overtime_pay = total_overtime * employee.hourly_rate * Config.OVERTIME_MULTIPLIER
            
            # Calculate gross salary
            gross_salary = base_salary + overtime_pay
            
            # Calculate deductions
            tax = gross_salary * Config.TAX_RATE
            
            # Create or update payroll
            payroll = Payroll.query.filter_by(
                employee_id=employee.id,
                month=month,
                year=year
            ).first()
            
            if payroll:
                # Update existing
                payroll.base_salary = base_salary
                payroll.overtime_pay = overtime_pay
                payroll.tax = tax
                payroll.work_days = work_days
                payroll.overtime_hours = total_overtime
            else:
                # Create new
                payroll = Payroll(
                    employee_id=employee.id,
                    month=month,
                    year=year,
                    base_salary=base_salary,
                    overtime_pay=overtime_pay,
                    tax=tax,
                    work_days=work_days,
                    overtime_hours=total_overtime
                )
                db.session.add(payroll)
            
            payroll.calculate_totals()
            db.session.commit()
            
            return True, payroll, "Payroll calculated successfully"
        
        except Exception as e:
            db.session.rollback()
            return False, None, f"Error calculating payroll: {str(e)}"
    
    def calculate_all_payrolls(self, month, year):
        """Calculate payroll for all active employees"""
        employees = Employee.query.filter_by(status='active').all()
        results = []
        
        for employee in employees:
            success, payroll, message = self.calculate_monthly_payroll(
                employee.employee_id,
                month,
                year
            )
            results.append({
                'employee': employee,
                'success': success,
                'payroll': payroll,
                'message': message
            })
        
        return results
    
    def approve_payroll(self, payroll_id):
        """Approve payroll"""
        try:
            payroll = Payroll.query.get(payroll_id)
            if not payroll:
                return False, "Payroll not found"
            
            payroll.status = 'approved'
            db.session.commit()

            AuditService.log(
                user_id=_acting_user_id(),
                action='payroll.approve',
                target_type='Payroll',
                target_id=payroll.id,
                target_label=payroll.employee.full_name,
                details=f'{payroll.month}/{payroll.year}, net salary {payroll.net_salary}.'
            )
            
            return True, "Payroll approved successfully"
        
        except Exception as e:
            db.session.rollback()
            return False, f"Error approving payroll: {str(e)}"
    
    def mark_paid(self, payroll_id):
        """Mark payroll as paid"""
        try:
            payroll = Payroll.query.get(payroll_id)
            if not payroll:
                return False, "Payroll not found"
            
            payroll.status = 'paid'
            payroll.paid_date = date.today()
            db.session.commit()

            AuditService.log(
                user_id=_acting_user_id(),
                action='payroll.mark_paid',
                target_type='Payroll',
                target_id=payroll.id,
                target_label=payroll.employee.full_name,
                details=f'{payroll.month}/{payroll.year}, net salary {payroll.net_salary}.'
            )
            
            return True, "Payroll marked as paid"
        
        except Exception as e:
            db.session.rollback()
            return False, f"Error marking payroll as paid: {str(e)}"
    
    def get_employee_payroll_history(self, employee_id):
        """Get employee payroll history"""
        employee = Employee.query.filter_by(employee_id=employee_id).first()
        if not employee:
            return []
        
        return Payroll.query.filter_by(employee_id=employee.id).order_by(
            Payroll.year.desc(),
            Payroll.month.desc()
        ).all()
    
    def get_payroll_summary(self, month, year):
        """Get payroll summary for a month"""
        payrolls = Payroll.query.filter_by(month=month, year=year).all()
        
        total_gross = sum(p.gross_salary for p in payrolls)
        total_net = sum(p.net_salary for p in payrolls)
        total_tax = sum(p.tax for p in payrolls)
        
        return {
            'total_employees': len(payrolls),
            'total_gross': total_gross,
            'total_net': total_net,
            'total_tax': total_tax,
            'payrolls': payrolls
        }