from datetime import datetime, timedelta
from sqlalchemy import func

from extensions import db
from models.employee import Employee
from models.attendance import Attendance
from models.department import Department
from models.emotion import Emotion


class AnalyticsService:
    """Chart-ready aggregates for the admin/HR dashboards."""

    @staticmethod
    def get_weekly_attendance_trend():
        """Present / late / absent counts for each of the last 7 days."""
        today = datetime.now().date()
        days = [today - timedelta(days=i) for i in range(6, -1, -1)]

        total_active = Employee.query.filter_by(status='active').count()

        labels, present, late, absent = [], [], [], []

        for d in days:
            day_present = Attendance.query.filter_by(date=d, status='present').count()
            day_late = Attendance.query.filter_by(date=d, status='late').count()
            day_absent = max(total_active - day_present - day_late, 0)

            labels.append(d.strftime('%a'))
            present.append(day_present)
            late.append(day_late)
            absent.append(day_absent)

        return {
            'labels': labels,
            'present': present,
            'late': late,
            'absent': absent,
        }

    @staticmethod
    def get_emotion_distribution(days=30):
        """How many times each emotion was detected in the last N days."""
        since = datetime.now() - timedelta(days=days)

        rows = db.session.query(
            Emotion.emotion, func.count(Emotion.id)
        ).filter(
            Emotion.detected_at >= since
        ).group_by(Emotion.emotion).all()

        labels = [(r[0] or 'unknown').capitalize() for r in rows]
        counts = [r[1] for r in rows]

        return {'labels': labels, 'counts': counts, 'has_data': bool(rows)}

    @staticmethod
    def get_department_headcount():
        """Active employee count per department."""
        rows = db.session.query(
            Department.name, func.count(Employee.id)
        ).join(
            Employee, Employee.department_id == Department.id
        ).filter(
            Employee.status == 'active'
        ).group_by(Department.name).all()

        labels = [r[0] for r in rows]
        counts = [r[1] for r in rows]

        return {'labels': labels, 'counts': counts, 'has_data': bool(rows)}

    @staticmethod
    def get_monthly_payroll_trend(months=6):
        """Total net payroll paid out for each of the last N months."""
        from models.payroll import Payroll

        today = datetime.now()
        points = []

        year, month = today.year, today.month
        for _ in range(months):
            points.append((year, month))
            month -= 1
            if month == 0:
                month = 12
                year -= 1

        points.reverse()

        labels, totals = [], []
        for y, m in points:
            total = db.session.query(func.coalesce(func.sum(Payroll.net_salary), 0)).filter(
                Payroll.year == y, Payroll.month == m
            ).scalar()

            labels.append(f"{['', 'Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][m]} {y}")
            totals.append(float(total or 0))

        return {'labels': labels, 'totals': totals}
