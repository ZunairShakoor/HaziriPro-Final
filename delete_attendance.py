from app import app
from extensions import db
from models.attendance import Attendance

with app.app_context():
    deleted = Attendance.query.delete()
    db.session.commit()

    print(f"Deleted {deleted} attendance records successfully!")