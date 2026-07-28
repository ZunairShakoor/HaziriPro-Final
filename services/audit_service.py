from extensions import db
from models.audit_log import AuditLog


class AuditService:
    """
    Records who did what to sensitive records (employee deletion, salary
    edits, leave/payroll approvals, etc). Call log() right alongside the
    db.session.commit() for the action being recorded.
    """

    @staticmethod
    def log(user_id, action, target_type=None, target_id=None, target_label=None, details=None):
        try:
            entry = AuditLog(
                user_id=user_id,
                action=action,
                target_type=target_type,
                target_id=str(target_id) if target_id is not None else None,
                target_label=target_label,
                details=details,
            )
            db.session.add(entry)
            db.session.commit()
        except Exception:
            # Never let audit logging itself break the calling action.
            db.session.rollback()

    @staticmethod
    def get_recent(limit=100):
        return AuditLog.query.order_by(AuditLog.created_at.desc()).limit(limit).all()

    @staticmethod
    def get_paginated(page=1, per_page=25):
        return AuditLog.query.order_by(AuditLog.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
