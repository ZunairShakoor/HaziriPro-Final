from flask import (
    Blueprint,
    render_template,
    request,
    send_file,
    flash,
    redirect,
    url_for,
)
from flask_login import login_required
from datetime import datetime, timedelta

from services.report_service import ReportService
from utils.permissions import hr_required

reports_bp = Blueprint("reports", __name__)

report_service = ReportService()


# =====================================================
# Attendance Report Page
# =====================================================
@reports_bp.route("/attendance")
@login_required
@hr_required
def attendance():

    today = datetime.today().date()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)

    return render_template(
        "reports/attendance.html",
        today=today.strftime("%Y-%m-%d"),
        week_start=week_start.strftime("%Y-%m-%d"),
        month_start=month_start.strftime("%Y-%m-%d"),
    )


# =====================================================
# Generate Attendance Report
# =====================================================
@reports_bp.route("/attendance/generate", methods=["POST"])
@login_required
@hr_required
def generate_attendance():

    try:

        report_format = request.form.get("format", "pdf")

        start_date = request.form.get("start_date", "").strip()
        end_date = request.form.get("end_date", "").strip()

        if not start_date or not end_date:
            flash("Please select both Start Date and End Date.", "warning")
            return redirect(url_for("reports.attendance"))

        start_date = datetime.strptime(
            start_date,
            "%Y-%m-%d"
        ).date()

        end_date = datetime.strptime(
            end_date,
            "%Y-%m-%d"
        ).date()

        filepath = report_service.generate_attendance_report(
            start_date,
            end_date,
            report_format
        )

        return send_file(
            filepath,
            as_attachment=True,
            download_name=f"attendance_report.{report_format if report_format != 'excel' else 'xlsx'}"
        )

    except Exception as e:

        flash(f"Error generating report: {str(e)}", "danger")
        return redirect(url_for("reports.attendance"))
    # =====================================================
# Payroll Report Page
# =====================================================
@reports_bp.route("/payroll")
@login_required
@hr_required
def payroll():
    return render_template("reports/payroll.html")


# =====================================================
# Generate Payroll Report
# =====================================================
@reports_bp.route("/payroll/generate", methods=["POST"])
@login_required
@hr_required
def generate_payroll():

    try:

        month = int(request.form.get("month"))
        year = int(request.form.get("year"))
        report_format = request.form.get("format", "pdf")

        filepath = report_service.generate_payroll_report(
            month,
            year,
            report_format
        )

        extension = "xlsx" if report_format == "excel" else report_format

        return send_file(
            filepath,
            as_attachment=True,
            download_name=f"payroll_report_{month}_{year}.{extension}"
        )

    except Exception as e:
        flash(f"Error generating payroll report: {e}", "danger")
        return redirect(url_for("reports.payroll"))


# =====================================================
# Employee Report Page
# =====================================================
@reports_bp.route("/employees")
@login_required
@hr_required
def employees():
    return render_template("reports/employees.html")


# =====================================================
# Generate Employee Report
# =====================================================
@reports_bp.route("/employees/generate", methods=["POST"])
@login_required
@hr_required
def generate_employees():

    try:

        report_format = request.form.get("format", "pdf")

        filepath = report_service.generate_employee_report(
            report_format
        )

        extension = "xlsx" if report_format == "excel" else report_format

        return send_file(
            filepath,
            as_attachment=True,
            download_name=f"employee_report.{extension}"
        )

    except Exception as e:
        flash(f"Error generating employee report: {e}", "danger")
        return redirect(url_for("reports.employees"))
    # =====================================================
# Emotion Report Page
# =====================================================
@reports_bp.route("/emotions")
@login_required
@hr_required
def emotions():
    return render_template("reports/emotions.html")


# =====================================================
# Generate Emotion Report
# =====================================================
@reports_bp.route("/emotions/generate", methods=["POST"])
@login_required
@hr_required
def generate_emotions():

    try:

        report_format = request.form.get("format", "pdf")

        start_date = request.form.get("start_date", "").strip()
        end_date = request.form.get("end_date", "").strip()

        if not start_date or not end_date:
            flash("Please select both Start Date and End Date.", "warning")
            return redirect(url_for("reports.emotions"))

        start_date = datetime.strptime(
            start_date,
            "%Y-%m-%d"
        ).date()

        end_date = datetime.strptime(
            end_date,
            "%Y-%m-%d"
        ).date()

        filepath = report_service.generate_emotion_report(
            start_date,
            end_date,
            report_format
        )

        extension = "xlsx" if report_format == "excel" else report_format

        return send_file(
            filepath,
            as_attachment=True,
            download_name=f"emotion_report.{extension}"
        )

    except Exception as e:
        flash(f"Error generating emotion report: {e}", "danger")
        return redirect(url_for("reports.emotions"))