from models.department import Department
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from services.attendance_service import AttendanceService
from models.employee import Employee
from models.attendance import Attendance
from utils.permissions import hr_required
import base64

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except Exception:
    cv2 = None
    np = None
    CV2_AVAILABLE = False

attendance_bp = Blueprint('attendance', __name__)
attendance_service = AttendanceService()

@attendance_bp.route('/live')
@login_required
def live():
    return render_template('attendance/live.html')

@attendance_bp.route('/check-in', methods=['POST'])
@login_required
def check_in():
    if not CV2_AVAILABLE:
        return jsonify({
            'success': False,
            'message': 'Camera-based check-in is unavailable because opencv-python '
                       'failed to install. Ask your admin to check the server setup.'
        })

    try:
        # Get image from request
        image_data = request.json.get('image')
        
        if not image_data:
            return jsonify({'success': False, 'message': 'No image provided'})
        
        # Decode base64 image
        image_data = image_data.split(',')[1]
        image_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Check in
        success, employee, message = attendance_service.check_in(image_array=image)
        
        if success:
            return jsonify({
                "success": True,
                "employee": {
                "id": employee.employee_id,
                "name": employee.full_name
            },
        "message": message["message"],
        "emotion": message["emotion"],
        "emotion_confidence": round(message["emotion_confidence"], 2),
        "face_confidence": round(message["face_confidence"] * 100, 2),
        "quote": message["quote"]
        })
        else:
            return jsonify({'success': False, 'message': message})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@attendance_bp.route('/check-out', methods=['POST'])
@login_required
def check_out():
    if not CV2_AVAILABLE:
        return jsonify({
            'success': False,
            'message': 'Camera-based check-out is unavailable because opencv-python '
                       'failed to install. Ask your admin to check the server setup.'
        })

    try:
        # Get image from request
        image_data = request.json.get('image')
        
        if not image_data:
            return jsonify({'success': False, 'message': 'No image provided'})
        
        # Decode base64 image
        image_data = image_data.split(',')[1]
        image_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        # Check out
        success, employee, message = attendance_service.check_out(image_array=image)
        
        if success:
            return jsonify({
                 "success": True,
                "employee": {
                    "id": employee.employee_id,
                     "name": employee.full_name
                     },
                 "message": message["message"],
                "emotion": message["emotion"],
                "emotion_confidence": round(message["emotion_confidence"], 2),
                "face_confidence": message.get("face_confidence"),
                "work_hours": round(message.get("work_hours", 0), 2),
                "quote": message["quote"]
            })
        else:
            return jsonify({'success': False, 'message': message})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@attendance_bp.route('/history')
@login_required
def history():

    # -----------------------------
    # Filters
    # -----------------------------
    employee_code = request.args.get("employee_id", "")
    department_id = request.args.get("department", "")
    status = request.args.get("status", "")

    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    if start_date:
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    else:
        start_date = datetime.now().replace(day=1).date()

    if end_date:
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
    else:
        end_date = datetime.now().date()

    # -----------------------------
    # Base Query
    # -----------------------------
    query = Attendance.query.join(Employee).filter(
        Attendance.date >= start_date,
        Attendance.date <= end_date
    )

    # -----------------------------
    # Employee Filter
    # -----------------------------
    if employee_code:
        employee = Employee.query.filter_by(
            employee_id=employee_code
        ).first()

        if employee:
            query = query.filter(
                Attendance.employee_id == employee.id
            )

    # -----------------------------
    # Department Filter
    # -----------------------------
    if department_id:
        query = query.filter(
            Employee.department_id == int(department_id)
        )

    # -----------------------------
    # Status Filter
    # -----------------------------
    if status:
        query = query.filter(
            Attendance.status == status
        )

    # -----------------------------
    # Employee Login Restriction
    # -----------------------------
    if current_user.role == "employee":

        employee = Employee.query.filter_by(
            user_id=current_user.id
        ).first()

        if employee:
            query = query.filter(
                Attendance.employee_id == employee.id
            )

    # -----------------------------
    # Fetch Data
    # -----------------------------
    page = request.args.get("page", 1, type=int)
    pagination = query.order_by(
        Attendance.date.desc(),
        Attendance.check_in.desc()
    ).paginate(page=page, per_page=25, error_out=False)
    attendances = pagination.items

    employees = []
    departments = []

    if current_user.role in ["admin", "hr"]:

        employees = Employee.query.filter_by(
            status="active"
        ).order_by(Employee.first_name).all()

        departments = Department.query.order_by(
            Department.name
        ).all()

    return render_template(
        "attendance/history.html",
        attendances=attendances,
        pagination=pagination,
        employees=employees,
        departments=departments,
        start_date=start_date,
        end_date=end_date,
        selected_department=department_id,
        selected_status=status
    )

@attendance_bp.route('/reports')
@login_required
@hr_required
def reports():
    today = datetime.now().date()
    
    # Daily summary
    daily_summary = attendance_service.get_daily_attendance_summary(today)
    
    # Weekly summary
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    
    weekly_attendances = Attendance.query.filter(
        Attendance.date >= week_start,
        Attendance.date <= week_end
    ).all()
    
    return render_template('attendance/reports.html',
                         daily_summary=daily_summary,
                         weekly_attendances=weekly_attendances)

@attendance_bp.route('/manual-mark', methods=['POST'])
@login_required
@hr_required
def manual_mark():
    employee_id = request.form.get('employee_id')
    date_str = request.form.get('date')
    status = request.form.get('status')
    notes = request.form.get('notes')
    
    date = datetime.strptime(date_str, '%Y-%m-%d').date()
    
    success, message = attendance_service.mark_manual_attendance(
        employee_id, date, status, notes
    )
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('attendance.history'))