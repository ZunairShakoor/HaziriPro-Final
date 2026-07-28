from datetime import datetime
from extensions import db

class Emotion(db.Model):
    __tablename__ = 'emotions'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    
    # Emotion Details
    emotion = db.Column(db.String(50))  # happy, sad, angry, neutral, etc.
    confidence = db.Column(db.Float)
    detected_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Context
    context = db.Column(db.String(100))  # check-in, check-out, during-work
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Emotion {self.employee_id} - {self.emotion}>'