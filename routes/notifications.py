from flask import Blueprint, render_template, jsonify, redirect, url_for, request
from flask_login import login_required, current_user

from services.notification_service import NotificationService

notifications_bp = Blueprint('notifications', __name__)


# ==========================================================
# Full notifications page
# ==========================================================
@notifications_bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    pagination = NotificationService.get_paginated(current_user.id, page=page, per_page=20)
    return render_template('notifications/list.html', pagination=pagination, notifications=pagination.items)


# ==========================================================
# Recent notifications (for the navbar bell dropdown)
# ==========================================================
@notifications_bp.route('/recent')
@login_required
def recent():
    notifications = NotificationService.get_recent(current_user.id, limit=8)
    return jsonify({
        'success': True,
        'unread_count': NotificationService.unread_count(current_user.id),
        'notifications': [n.to_dict() for n in notifications],
    })


# ==========================================================
# Unread count only (cheap polling endpoint)
# ==========================================================
@notifications_bp.route('/unread-count')
@login_required
def unread_count():
    return jsonify({
        'success': True,
        'unread_count': NotificationService.unread_count(current_user.id),
    })


# ==========================================================
# Mark one notification as read, then go to its link (if any)
# ==========================================================
@notifications_bp.route('/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_read(notification_id):
    NotificationService.mark_read(notification_id, current_user.id)
    return jsonify({'success': True})


# ==========================================================
# Mark one as read AND redirect to its link — used for plain
# (non-JS) navigation, e.g. clicking a notification on the full list page
# ==========================================================
@notifications_bp.route('/<int:notification_id>/open')
@login_required
def open_notification(notification_id):
    from models.notification import Notification
    notification = Notification.query.filter_by(id=notification_id, user_id=current_user.id).first()

    if not notification:
        return redirect(url_for('notifications.index'))

    if not notification.is_read:
        NotificationService.mark_read(notification.id, current_user.id)

    return redirect(notification.link or url_for('notifications.index'))


# ==========================================================
# Mark all as read
# ==========================================================
@notifications_bp.route('/mark-all-read', methods=['POST'])
@login_required
def mark_all_read():
    NotificationService.mark_all_read(current_user.id)
    return jsonify({'success': True})
