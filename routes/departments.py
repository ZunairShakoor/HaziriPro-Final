from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from extensions import db
from models.department import Department
from models.employee import Employee
from utils.permissions import hr_required
from services.audit_service import AuditService

departments_bp = Blueprint("departments", __name__)


@departments_bp.route("/")
@login_required
def list():
    departments = Department.query.order_by(Department.name).all()
    return render_template(
        "departments/list.html",
        departments=departments
    )


@departments_bp.route("/add", methods=["GET", "POST"])
@login_required
@hr_required
def add():

    if request.method == "POST":

        name = request.form.get("name")
        code = request.form.get("code")
        description = request.form.get("description")
        manager_id = request.form.get("manager_id")

        if Department.query.filter_by(code=code).first():
            flash("Department code already exists.", "danger")
            return redirect(url_for("departments.add"))

        department = Department(
            name=name,
            code=code,
            description=description,
            manager_id=manager_id if manager_id else None,
        )

        db.session.add(department)
        db.session.commit()

        flash("Department created successfully.", "success")
        return redirect(url_for("departments.list"))

    employees = Employee.query.filter_by(status="active").all()

    return render_template(
        "departments/create.html",
        employees=employees
    )


@departments_bp.route("/<int:department_id>/edit", methods=["GET", "POST"])
@login_required
@hr_required
def edit(department_id):

    department = Department.query.get_or_404(department_id)

    if request.method == "POST":

        department.name = request.form.get("name")
        department.code = request.form.get("code")
        department.description = request.form.get("description")

        manager_id = request.form.get("manager_id")
        department.manager_id = manager_id if manager_id else None

        db.session.commit()

        flash("Department updated successfully.", "success")
        return redirect(url_for("departments.list"))

    employees = Employee.query.filter_by(status="active").all()

    return render_template(
        "departments/edit.html",
        department=department,
        employees=employees
    )


@departments_bp.route("/<int:department_id>/delete", methods=["POST"])
@login_required
@hr_required
def delete(department_id):

    department = Department.query.get_or_404(department_id)

    if department.employees:
        flash(
            "Cannot delete a department that still has employees.",
            "danger",
        )
        return redirect(url_for("departments.list"))

    department_name = department.name

    db.session.delete(department)
    db.session.commit()

    AuditService.log(
        user_id=current_user.id,
        action='department.delete',
        target_type='Department',
        target_id=department_id,
        target_label=department_name,
    )

    flash("Department deleted successfully.", "success")
    return redirect(url_for("departments.list"))