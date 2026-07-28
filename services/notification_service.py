from extensions import db
from models.user import User
from models.notification import Notification


class NotificationService:
    """
    Central place to create notifications. Other services/routes call these
    helpers instead of touching the Notification model directly, so the
    triggers (leave, employees, attendance, payroll...) stay one-liners.
    """

    @staticmethod
    def notify_user(user_id, title, message=None, category='system', icon='bell', link=None):
        """Create a single notification for one user."""
        if not user_id:
            return None

        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            category=category,
            icon=icon,
            link=link,
        )
        db.session.add(notification)
        db.session.commit()
        return notification

    @staticmethod
    def notify_roles(roles, title, message=None, category='system', icon='bell', link=None, exclude_user_id=None):
        """Create the same notification for every active user in the given roles."""
        query = User.query.filter(User.role.in_(roles), User.is_active.is_(True))

        if exclude_user_id:
            query = query.filter(User.id != exclude_user_id)

        users = query.all()

        notifications = []
        for user in users:
            notifications.append(
                Notification(
                    user_id=user.id,
                    title=title,
                    message=message,
                    category=category,
                    icon=icon,
                    link=link,
                )
            )

        if notifications:
            db.session.add_all(notifications)
            db.session.commit()

        return notifications

    @staticmethod
    def get_recent(user_id, limit=10):
        return Notification.query.filter_by(user_id=user_id) \
            .order_by(Notification.created_at.desc()) \
            .limit(limit).all()

    @staticmethod
    def get_all(user_id):
        return Notification.query.filter_by(user_id=user_id) \
            .order_by(Notification.created_at.desc()).all()

    @staticmethod
    def get_paginated(user_id, page=1, per_page=20):
        return Notification.query.filter_by(user_id=user_id) \
            .order_by(Notification.created_at.desc()) \
            .paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def unread_count(user_id):
        return Notification.query.filter_by(user_id=user_id, is_read=False).count()

    @staticmethod
    def mark_read(notification_id, user_id):
        notification = Notification.query.filter_by(id=notification_id, user_id=user_id).first()
        if not notification:
            return False
        notification.is_read = True
        db.session.commit()
        return True

    @staticmethod
    def mark_all_read(user_id):
        Notification.query.filter_by(user_id=user_id, is_read=False).update({'is_read': True})
        db.session.commit()
