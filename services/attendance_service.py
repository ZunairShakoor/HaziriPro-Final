from flask_login import current_user
from datetime import datetime, date, timedelta
from extensions import db
from models.attendance import Attendance
from models.employee import Employee
from ai.face_recognition import FaceRecognitionSystem
from ai.emotion_detector import EmotionDetector
from models.emotion import Emotion
from services.quote_service import QuoteService
from services.notification_service import NotificationService

class AttendanceService:
    def __init__(self):
        self.face_recognition = FaceRecognitionSystem()
        self.emotion_detector = EmotionDetector()

    def _get_emotion_input(self, image_array):
        """
        Crop tightly to the detected face (with a small margin) before
        handing the image to the emotion detector. Analyzing a whole
        webcam frame (background, desk, etc.) instead of just the face
        is the main reason emotion detection tends to default to
        "neutral" regardless of actual expression — DeepFace performs
        much better on a tight, well-cropped face image.

        Falls back to the original full frame if a face location can't
        be determined (e.g. dependency unavailable), so emotion
        detection still runs, just less accurately.
        """
        if image_array is None:
            return image_array

        location = self.face_recognition.get_face_location(image_array)
        if not location:
            return image_array

        top, right, bottom, left = location
        height, width = image_array.shape[:2]

        margin_y = int((bottom - top) * 0.25)
        margin_x = int((right - left) * 0.25)

        top = max(0, top - margin_y)
        left = max(0, left - margin_x)
        bottom = min(height, bottom + margin_y)
        right = min(width, right + margin_x)

        crop = image_array[top:bottom, left:right]
        return crop if crop.size > 0 else image_array
    
    def check_in(self, image_path=None, image_array=None):
        """Check in employee using face verification"""
        try:
            employee = current_user.employee

            if not employee:
                return False, None, "Employee record not found."

            verified, confidence, message = self.face_recognition.verify_face(
                employee.employee_id,
                image_path=image_path,
                image_array=image_array,
            )

            if not verified:
                return False, None, message

            today = date.today()
            existing_attendance = Attendance.query.filter_by(
                employee_id=employee.id,
                date=today
            ).first()

            if existing_attendance and existing_attendance.check_in:
                return False, None, "Already checked in today"

            emotion, emotion_confidence, _ = self.emotion_detector.detect_emotion(
                image_path=image_path,
                image_array=self._get_emotion_input(image_array)
            )

            quote = QuoteService.get_quote(emotion)

            if not existing_attendance:
                attendance = Attendance(
                    employee_id=employee.id,
                    date=today,
                    check_in=datetime.now(),
                    status="present"
                )
                db.session.add(attendance)
            else:
                existing_attendance.check_in = datetime.now()
                existing_attendance.status = "present"
                attendance = existing_attendance

            work_start_time = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
            grace_period = timedelta(minutes=15)

            if attendance.check_in > (work_start_time + grace_period):
                attendance.is_late = True
                attendance.late_minutes = int((attendance.check_in - work_start_time).total_seconds() / 60)
                attendance.status = "late"

            if emotion:
                db.session.add(
                    Emotion(
                        employee_id=employee.id,
                        emotion=emotion,
                        confidence=emotion_confidence,
                        context="check-in"
                    )
                )

            db.session.commit()

            if attendance.is_late:
                NotificationService.notify_roles(
                    roles=['admin', 'hr', 'manager'],
                    title='Late check-in',
                    message=f'{employee.full_name} checked in {attendance.late_minutes} minute(s) late.',
                    category='attendance',
                    icon='clock',
                    link='/attendance/history',
                )

            return True, employee, {
                "message": "Check-in Successful!",
                "face_confidence": confidence,
                "emotion": emotion,
                "emotion_confidence": emotion_confidence,
                "quote": quote,
            }

        except Exception as e:
            db.session.rollback()
            return False, None, f"Error during check-in: {e}"
        
    def check_out(self, image_path=None, image_array=None):
            """Check out employee using face verification"""
            try:
                employee = current_user.employee
    
                if not employee:
                    return False, None, "Employee record not found."
    
                verified, confidence, message = self.face_recognition.verify_face(
                    employee.employee_id,
                    image_path=image_path,
                    image_array=image_array,
                )
    
                if not verified:
                    return False, None, message
    
                today = date.today()
                attendance = Attendance.query.filter_by(
                    employee_id=employee.id,
                    date=today
                ).first()
    
                if not attendance or not attendance.check_in:
                    return False, None, "No check-in record found for today"
    
                if attendance.check_out:
                    return False, None, "Already checked out today"
    
                attendance.check_out = datetime.now()
                attendance.calculate_work_hours()
    
                if attendance.work_hours > 8:
                    attendance.overtime_hours = attendance.work_hours - 8
    
                emotion, emotion_confidence, _ = self.emotion_detector.detect_emotion(
                    image_path=image_path,
                    image_array=self._get_emotion_input(image_array)
                )
    
                quote = QuoteService.get_quote(emotion)
    
                if emotion:
                    db.session.add(
                        Emotion(
                            employee_id=employee.id,
                            emotion=emotion,
                            confidence=emotion_confidence,
                            context="check-out"
                        )
                    )
    
                db.session.commit()
    
                return True, employee, {
                    "message": "Check-out Successful!",
                    "emotion": emotion,
                    "emotion_confidence": emotion_confidence,
                    "work_hours": attendance.work_hours,
                    "quote": quote,
                }
    
            except Exception as e:
                db.session.rollback()
                return False, None, f"Error during check-out: {e}"
            
    def get_attendance_by_date(self, employee_id, date):
        """Get attendance for specific date"""
        employee = Employee.query.filter_by(employee_id=employee_id).first()
        if not employee:
            return None
        
        return Attendance.query.filter_by(
            employee_id=employee.id,
            date=date
        ).first()
    
    def get_employee_attendance_history(self, employee_id, start_date=None, end_date=None):
        """Get employee attendance history"""
        employee = Employee.query.filter_by(employee_id=employee_id).first()
        if not employee:
            return []
        
        query = Attendance.query.filter_by(employee_id=employee.id)
        
        if start_date:
            query = query.filter(Attendance.date >= start_date)
        if end_date:
            query = query.filter(Attendance.date <= end_date)
        
        return query.order_by(Attendance.date.desc()).all()
    
    def get_daily_attendance_summary(self, date=None):
        """Get daily attendance summary"""
        if not date:
            date = datetime.now().date()
        
        total_employees = Employee.query.filter_by(status='active').count()
        
        present = Attendance.query.filter_by(
            date=date,
            status='present'
        ).count()
        
        late = Attendance.query.filter_by(
            date=date,
            status='late'
        ).count()
        
        absent = total_employees - (present + late)
        
        return {
            'total': total_employees,
            'present': present,
            'late': late,
            'absent': absent,
            'date': date
        }
    
    def mark_manual_attendance(self, employee_id, date, status, notes=None):
        """Manually mark attendance"""
        try:
            employee = Employee.query.filter_by(employee_id=employee_id).first()
            if not employee:
                return False, "Employee not found"
            
            # Check if attendance already exists
            attendance = Attendance.query.filter_by(
                employee_id=employee.id,
                date=date
            ).first()
            
            if attendance:
                attendance.status = status
                attendance.notes = notes
            else:
                attendance = Attendance(
                    employee_id=employee.id,
                    date=date,
                    status=status,
                    notes=notes
                )
                db.session.add(attendance)
            
            db.session.commit()

            if status == 'absent':
                NotificationService.notify_roles(
                    roles=['admin', 'hr'],
                    title='Employee marked absent',
                    message=f'{employee.full_name} was marked absent on {date}.',
                    category='attendance',
                    icon='calendar-times',
                    link='/attendance/history',
                )

            return True, "Attendance marked successfully"
        
        except Exception as e:
            db.session.rollback()
            return False, f"Error marking attendance: {str(e)}"