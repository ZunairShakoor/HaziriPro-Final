import re
from datetime import datetime, date
from models.employee import Employee
from models.attendance import Attendance
from models.payroll import Payroll
from models.leave import Leave

EMPLOYEE_ID_PATTERN = re.compile(r'\bEMP\d{6}\b', re.IGNORECASE)


class ChatbotService:
    def __init__(self, employee_id=None):
        self.employee_id = employee_id
        self.employee = None
        if employee_id:
            self.employee = Employee.query.filter_by(employee_id=employee_id).first()

    def process_query(self, query):
        """Process user query and return response"""
        original_query = query

        # If we don't already know who's asking, see if the message itself
        # contains an employee ID (e.g. the user typing "EMP622959" in
        # response to "Please provide your employee ID"). Previously this
        # was never checked, so providing the ID always fell through to
        # "I'm not sure I understand."
        if not self.employee:
            match = EMPLOYEE_ID_PATTERN.search(original_query)
            if match:
                found_id = match.group(0).upper()
                employee = Employee.query.filter_by(employee_id=found_id).first()

                if employee:
                    self.employee = employee
                    self.employee_id = found_id

                    # If the message was *just* the ID with no other intent
                    # (attendance/leave/salary/etc.), ask what they want
                    # instead of guessing.
                    remainder = EMPLOYEE_ID_PATTERN.sub('', original_query).strip()
                    if not remainder or not self._has_known_intent(remainder):
                        return (
                            f"Thanks, {employee.full_name}! I've got your record. "
                            "What would you like to know — today's attendance, "
                            "this month's attendance, leave status, salary, or your profile?"
                        )
                else:
                    return f"I couldn't find an employee with ID {found_id}. Please double-check it."

        query = query.lower().strip()
        
        # Attendance queries
        if 'attendance' in query or 'present' in query:
            return self._handle_attendance_query(query)
        
        # Leave queries
        elif 'leave' in query or 'vacation' in query:
            return self._handle_leave_query(query)
        
        # Salary queries
        elif 'salary' in query or 'payroll' in query or 'payment' in query:
            return self._handle_salary_query(query)
        
        # Employee info queries
        elif 'info' in query or 'profile' in query or 'details' in query:
            return self._handle_employee_info_query()
        
        # Help
        elif 'help' in query:
            return self._get_help_message()
        
        else:
            return "I'm not sure I understand. Type 'help' to see what I can do."

    @staticmethod
    def _has_known_intent(text):
        text = text.lower()
        keywords = [
            'attendance', 'present', 'leave', 'vacation',
            'salary', 'payroll', 'payment', 'info', 'profile', 'details', 'help'
        ]
        return any(k in text for k in keywords)
    
    def _handle_attendance_query(self, query):
        """Handle attendance-related queries"""
        if not self.employee:
            return "Please provide your employee ID to check attendance."
        
        if 'today' in query:
            today = date.today()
            attendance = Attendance.query.filter_by(
                employee_id=self.employee.id,
                date=today
            ).first()
            
            if attendance:
                if attendance.check_in and attendance.check_out:
                    return f"You checked in at {attendance.check_in.strftime('%H:%M')} and checked out at {attendance.check_out.strftime('%H:%M')}. Total work hours: {attendance.work_hours:.2f}"
                elif attendance.check_in:
                    return f"You checked in at {attendance.check_in.strftime('%H:%M')}. You haven't checked out yet."
                else:
                    return "No attendance record for today."
            else:
                return "You haven't checked in today."
        
        elif 'month' in query or 'this month' in query:
            today = date.today()
            start_date = today.replace(day=1)
            
            attendances = Attendance.query.filter(
                Attendance.employee_id == self.employee.id,
                Attendance.date >= start_date,
                Attendance.date <= today
            ).all()
            
            present_days = sum(1 for a in attendances if a.status in ['present', 'late'])
            late_days = sum(1 for a in attendances if a.status == 'late')
            total_hours = sum(a.work_hours or 0 for a in attendances)
            
            return f"This month: {present_days} days present, {late_days} days late, {total_hours:.2f} total work hours."
        
        return "Please specify if you want today's attendance or monthly summary."
    
    def _handle_leave_query(self, query):
        """Handle leave-related queries"""
        if not self.employee:
            return "Please provide your employee ID to check leave."
        
        if 'balance' in query or 'remaining' in query:
            # This would need leave balance tracking
            return "Leave balance feature coming soon!"
        
        elif 'status' in query or 'pending' in query:
            pending_leaves = Leave.query.filter_by(
                employee_id=self.employee.id,
                status='pending'
            ).all()
            
            if pending_leaves:
                leaves_text = "\n".join([
                    f"- {leave.leave_type}: {leave.start_date} to {leave.end_date} ({leave.days} days)"
                    for leave in pending_leaves
                ])
                return f"Pending leave requests:\n{leaves_text}"
            else:
                return "You have no pending leave requests."
        
        return "Ask about leave balance or pending requests."
    
    def _handle_salary_query(self, query):
        """Handle salary-related queries"""
        if not self.employee:
            return "Please provide your employee ID to check salary."
        
        today = date.today()
        
        if 'last' in query or 'latest' in query:
            # Get last month's payroll
            last_month = today.month - 1 if today.month > 1 else 12
            last_year = today.year if today.month > 1 else today.year - 1
            
            payroll = Payroll.query.filter_by(
                employee_id=self.employee.id,
                month=last_month,
                year=last_year
            ).first()
            
            if payroll:
                return f"Last month's salary:\nGross: Rs. {payroll.gross_salary:,.2f}\nNet: Rs. {payroll.net_salary:,.2f}\nStatus: {payroll.status}"
            else:
                return "No payroll record found for last month."
        
        elif 'this month' in query or 'current' in query:
            payroll = Payroll.query.filter_by(
                employee_id=self.employee.id,
                month=today.month,
                year=today.year
            ).first()
            
            if payroll:
                return f"This month's salary:\nGross: Rs. {payroll.gross_salary:,.2f}\nNet: Rs. {payroll.net_salary:,.2f}\nStatus: {payroll.status}"
            else:
                return "Payroll for this month hasn't been processed yet."
        
        return "Ask about this month's or last month's salary."
    
    def _handle_employee_info_query(self):
        """Handle employee information queries"""
        if not self.employee:
            return "Please provide your employee ID."
        
        info = f"""
Employee Information:
- Name: {self.employee.full_name}
- Employee ID: {self.employee.employee_id}
- Department: {self.employee.department.name if self.employee.department else 'N/A'}
- Position: {self.employee.position}
- Hire Date: {self.employee.hire_date}
- Employment Type: {self.employee.employment_type}
"""
        return info.strip()
    
    def _get_help_message(self):
        """Get help message"""
        return """
I can help you with:
- Attendance: "What's my attendance today?", "Show this month's attendance"
- Leave: "Check my leave status", "Show pending leaves"
- Salary: "What's my last salary?", "Show this month's salary"
- Profile: "Show my info", "My profile"

Just ask me anything!
"""