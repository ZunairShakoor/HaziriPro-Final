from datetime import datetime, timedelta
from sqlalchemy import func
from extensions import db
from models.attendance import Attendance
from models.employee import Employee
from models.payroll import Payroll
from models.emotion import Emotion
import pandas as pd
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import os

class ReportService:
    def generate_attendance_report(self, start_date, end_date, format='pdf'):
        """Generate attendance report"""
        attendances = Attendance.query.filter(
            Attendance.date >= start_date,
            Attendance.date <= end_date
        ).all()
        
        data = []
        for attendance in attendances:
            data.append({
                'Employee ID': attendance.employee.employee_id,
                'Name': attendance.employee.full_name,
                'Date': attendance.date,
                'Check In': attendance.check_in,
                'Check Out': attendance.check_out,
                'Status': attendance.status,
                'Work Hours': attendance.work_hours,
                'Overtime': attendance.overtime_hours
            })
        
        df = pd.DataFrame(data)
        
        if format == 'excel':
            return self._export_to_excel(df, 'attendance_report')
        elif format == 'csv':
            return self._export_to_csv(df, 'attendance_report')
        else:
            return self._export_to_pdf(df, 'Attendance Report', 'attendance_report')
    
    def generate_payroll_report(self, month, year, format='pdf'):
        """Generate payroll report"""
        payrolls = Payroll.query.filter_by(month=month, year=year).all()
        
        data = []
        for payroll in payrolls:
            data.append({
                'Employee ID': payroll.employee.employee_id,
                'Name': payroll.employee.full_name,
                'Base Salary': payroll.base_salary,
                'Overtime': payroll.overtime_pay,
                'Bonuses': payroll.bonuses,
                'Gross Salary': payroll.gross_salary,
                'Tax': payroll.tax,
                'Deductions': payroll.other_deductions,
                'Net Salary': payroll.net_salary,
                'Status': payroll.status
            })
        
        df = pd.DataFrame(data)
        
        if format == 'excel':
            return self._export_to_excel(df, f'payroll_report_{month}_{year}')
        elif format == 'csv':
            return self._export_to_csv(df, f'payroll_report_{month}_{year}')
        else:
            return self._export_to_pdf(df, f'Payroll Report - {month}/{year}', f'payroll_report_{month}_{year}')
    
    def generate_employee_report(self, format='pdf'):
        """Generate employee report"""
        employees = Employee.query.all()
        
        data = []
        for employee in employees:
            data.append({
                'Employee ID': employee.employee_id,
                'Name': employee.full_name,
                'Department': employee.department.name if employee.department else 'N/A',
                'Position': employee.position,
                'Hire Date': employee.hire_date,
                'Employment Type': employee.employment_type,
                'Status': employee.status,
                'Base Salary': employee.base_salary
            })
        
        df = pd.DataFrame(data)
        
        if format == 'excel':
            return self._export_to_excel(df, 'employee_report')
        elif format == 'csv':
            return self._export_to_csv(df, 'employee_report')
        else:
            return self._export_to_pdf(df, 'Employee Report', 'employee_report')
    
    def generate_emotion_report(self, start_date, end_date, format='pdf'):
        """Generate emotion analysis report"""
        emotions = Emotion.query.filter(
            Emotion.detected_at >= start_date,
            Emotion.detected_at <= end_date
        ).all()
        
        data = []
        for emotion in emotions:
            data.append({
                'Employee ID': emotion.employee.employee_id,
                'Name': emotion.employee.full_name,
                'Emotion': emotion.emotion,
                'Confidence': emotion.confidence,
                'Context': emotion.context,
                'Detected At': emotion.detected_at
            })
        
        df = pd.DataFrame(data)
        
        if format == 'excel':
            return self._export_to_excel(df, 'emotion_report')
        elif format == 'csv':
            return self._export_to_csv(df, 'emotion_report')
        else:
            return self._export_to_pdf(df, 'Emotion Analysis Report', 'emotion_report')
    
    def _export_to_excel(self, df, filename):
        """Export dataframe to Excel"""
        filepath = os.path.join('exports', 'excel', f'{filename}.xlsx')
        df.to_excel(filepath, index=False)
        return filepath
    
    def _export_to_csv(self, df, filename):
        """Export dataframe to CSV"""
        filepath = os.path.join('exports', 'csv', f'{filename}.csv')
        df.to_csv(filepath, index=False)
        return filepath
    
    def _export_to_pdf(self, df, title, filename):
        """Export dataframe to PDF"""
        filepath = os.path.join('exports', 'pdf', f'{filename}.pdf')
        
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        elements = []
        
        # Title
        styles = getSampleStyleSheet()
        title_para = Paragraph(title, styles['Title'])
        elements.append(title_para)
        elements.append(Spacer(1, 0.2*inch))
        
        # Table
        data = [df.columns.tolist()] + df.values.tolist()
        table = Table(data)
        
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        
        doc.build(elements)
        return filepath
    
    def get_attendance_statistics(self, start_date, end_date):
        """Get attendance statistics"""
        attendances = Attendance.query.filter(
            Attendance.date >= start_date,
            Attendance.date <= end_date
        ).all()
        
        total = len(attendances)
        present = sum(1 for a in attendances if a.status == 'present')
        late = sum(1 for a in attendances if a.status == 'late')
        absent = sum(1 for a in attendances if a.status == 'absent')
        
        avg_work_hours = sum(a.work_hours or 0 for a in attendances) / total if total > 0 else 0
        total_overtime = sum(a.overtime_hours or 0 for a in attendances)
        
        return {
            'total': total,
            'present': present,
            'late': late,
            'absent': absent,
            'present_percentage': (present / total * 100) if total > 0 else 0,
            'late_percentage': (late / total * 100) if total > 0 else 0,
            'absent_percentage': (absent / total * 100) if total > 0 else 0,
            'avg_work_hours': avg_work_hours,
            'total_overtime': total_overtime
        }