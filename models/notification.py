from datetime import datetime
from extensions import db


class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    title = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text)

    # leave, employee, attendance, payroll, system ...
    category = db.Column(db.String(30), default='system', index=True)

    # icon shown in the bell dropdown (Font Awesome class, without 'fas fa-')
    icon = db.Column(db.String(50), default='bell')

    # Optional link the notification should navigate to when clicked
    link = db.Column(db.String(255))

    is_read = db.Column(db.Boolean, default=False, index=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    user = db.relationship('User', backref=db.backref('notifications', lazy=True, cascade='all, delete-orphan'))

    def __repr__(self):
        return f'<Notification {self.id} - {self.title}>'

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'category': self.category,
            'icon': self.icon,
            'link': self.link,
            'is_read': self.is_read,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else None,
        }
