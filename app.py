from flask import Flask, render_template, redirect, url_for
from flask_login import current_user
from config import Config
from extensions import db, login_manager, migrate, csrf
import os
import click

# ============================================
# Create necessary directories FIRST
# ============================================
REQUIRED_DIRS = [
    "instance",
    "static/uploads/employees",
    "static/uploads/faces",
    "static/css",
    "static/js",
    "static/images",
    "exports/pdf",
    "exports/excel",
    "exports/csv",
    "ai",
    "templates/layouts",
    "templates/auth",
    "templates/dashboard",
    "templates/employees",
    "templates/departments",
    "templates/attendance",
    "templates/payroll",
    "templates/leave",
    "templates/reports",
    "templates/chatbot",
    "templates/settings",
    "templates/errors",
]

print("=" * 60)
print("HaziriPro - Smart Attendance System")
print("=" * 60)

for directory in REQUIRED_DIRS:
    os.makedirs(directory, exist_ok=True)


def create_app(config_class=Config):
    app = Flask(__name__)

    app.config.from_object(config_class)

    # Create folders
    Config.init_app(app)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    if app.config.get('SECRET_KEY') == 'dev-secret-key-change-this-in-production':
        print(
            "\n⚠️  WARNING: SECRET_KEY is still the insecure default from config.py.\n"
            "   Sessions and CSRF tokens are NOT safe like this in production.\n"
            "   Set a real SECRET_KEY via the SECRET_KEY environment variable "
            "(e.g. in a .env file) before deploying.\n"
        )

    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "info"

    # Import models AFTER db.init_app()
    from models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # ===========================
    # Register Blueprints
    # ===========================
    blueprints = [
        ("routes.auth", "auth_bp", "/auth"),
        ("routes.dashboard", "dashboard_bp", "/dashboard"),
        ("routes.employees", "employees_bp", "/employees"),
        ("routes.departments", "departments_bp", "/departments"),
        ("routes.attendance", "attendance_bp", "/attendance"),
        ("routes.payroll", "payroll_bp", "/payroll"),
        ("routes.leave", "leave_bp", "/leave"),
        ("routes.reports", "reports_bp", "/reports"),
        ("routes.chatbot", "chatbot_bp", "/chatbot"),
        ("routes.settings", "settings_bp", "/settings"),
        ("routes.notifications", "notifications_bp", "/notifications"),
    ]

    print("\nRegistering blueprints...")

    for module_name, blueprint_name, prefix in blueprints:
        try:
            module = __import__(module_name, fromlist=[blueprint_name])
            blueprint = getattr(module, blueprint_name)
            app.register_blueprint(blueprint, url_prefix=prefix)
            print(f"✓ {blueprint_name}")
        except Exception as e:
            print(f"✗ {blueprint_name}: {e}")

    # ===========================
    # Database
    # ===========================
    with app.app_context():
        db.create_all()
        create_default_admin()

    # ===========================
    # Routes
    # ===========================
    @app.route("/")
    def index():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard.index"))
        return redirect(url_for("auth.login"))

    # ===========================
    # Error Pages
    # ===========================
    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(403)
    def forbidden(error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(500)
    def internal(error):
        db.session.rollback()
        return render_template("errors/500.html"), 500

    # ===========================
    # Template Filters
    # ===========================
    @app.template_filter("datetime")
    def datetime_filter(value, fmt="%Y-%m-%d %H:%M"):
        if value is None:
            return ""
        return value.strftime(fmt)

    @app.template_filter("date")
    def date_filter(value, fmt="%Y-%m-%d"):
        if value is None:
            return ""
        return value.strftime(fmt)

    @app.template_filter("currency")
    def currency_filter(value):
        if value is None:
            return "Rs. 0.00"
        return f"Rs. {value:,.2f}"

    @app.context_processor
    def inject_now():
        from datetime import datetime
        return {"now": datetime.now()}

    @app.context_processor
    def inject_notifications():
        if current_user.is_authenticated:
            from services.notification_service import NotificationService
            return {
                "unread_notifications_count": NotificationService.unread_count(current_user.id)
            }
        return {"unread_notifications_count": 0}

    # ===========================
    # CLI Commands
    # ===========================
    @app.cli.command("mark-absentees")
    @click.option('--date', 'date_str', default=None, help='Date to check, YYYY-MM-DD (defaults to today).')
    def mark_absentees_command(date_str):
        """
        Mark any active employee who never checked in on the given date as
        'absent', and notify admin/hr. Meant to be run once per day, after
        work hours, via Windows Task Scheduler or cron:

            python -m flask --app app mark-absentees

        This isn't run automatically by the web server itself — there's no
        background scheduler wired into this project. Running it manually
        (or via a scheduled task) is what actually flags no-shows; without
        it, "absent" only ever gets set when someone is manually marked
        absent from the Attendance screen.
        """
        from datetime import datetime as dt
        from models.employee import Employee
        from models.attendance import Attendance
        from services.notification_service import NotificationService

        target_date = dt.strptime(date_str, '%Y-%m-%d').date() if date_str else dt.now().date()

        active_employees = Employee.query.filter_by(status='active').all()
        marked = []

        for employee in active_employees:
            existing = Attendance.query.filter_by(employee_id=employee.id, date=target_date).first()
            if existing:
                continue  # already has a record (present/late/leave/manual absent)

            db.session.add(Attendance(
                employee_id=employee.id,
                date=target_date,
                status='absent',
                notes='Auto-marked: no check-in recorded.'
            ))
            marked.append(employee)

        db.session.commit()

        if marked:
            names = ', '.join(e.full_name for e in marked[:10])
            more = f' and {len(marked) - 10} more' if len(marked) > 10 else ''
            NotificationService.notify_roles(
                roles=['admin', 'hr'],
                title=f'{len(marked)} employee(s) marked absent',
                message=f'No check-in recorded for {target_date}: {names}{more}.',
                category='attendance',
                icon='calendar-times',
                link='/attendance/history',
            )

        print(f"Marked {len(marked)} employee(s) absent for {target_date}.")

    return app


def create_default_admin():
    from models.user import User
    from werkzeug.security import generate_password_hash

    admin = User.query.filter_by(username="admin").first()

    if admin is None:
        admin = User(
            username="admin",
            email="admin@haziripro.com",
            password_hash=generate_password_hash("admin123"),
            role="admin",
            is_active=True,
        )

        db.session.add(admin)
        db.session.commit()

        print("\nDefault admin created")
        print("Username: admin")
        print("Password: admin123")


app = create_app()

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
        use_reloader=False
    )