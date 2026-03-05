from flask import (
    Blueprint, render_template, request,
    redirect, url_for, session, flash, abort, make_response,current_app,make_response,Response
)
from models import (
    db, Student, StudentMarks,
    SubjectMaster, Result, User, TeacherAssignment
)
from utils.decorators import login_required
import pdfkit
import os
from utils.pdf_utils import generate_result_pdf


bp = Blueprint("student", __name__, url_prefix="/student")

@bp.route("/dashboard")
@login_required("student")
def student_dashboard():

    student = Student.query.filter_by(
        user_id=session["user_id"]
    ).first_or_404()

    subjects = SubjectMaster.query.filter_by(
        course_id=student.course_id,
        year_id=student.year_id
    ).all()

    marks = StudentMarks.query.filter_by(
        student_id=student.id
    ).all()

    marks_map = {m.subject_id: m.marks for m in marks}

    assignments = TeacherAssignment.query.filter_by(
        course_id=student.course_id,
        year_id=student.year_id,
        division_id=student.division_id
    ).all()

    teacher_map = {
        a.subject_id: a.teacher.username
        for a in assignments
    }

    return render_template(
        "student/dashboard.html",
        student=student,
        subjects=subjects,
        marks_map=marks_map,
        teacher_map=teacher_map
    )

@bp.route("/change-password", methods=["GET", "POST"])
@login_required("student")
def change_password():

    user = User.query.get_or_404(session["user_id"])

    if request.method == "POST":
        old_password = request.form.get("old_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        if user.password != old_password:
            flash("Old password is incorrect", "danger")
            return redirect(url_for("student.change_password"))

        if new_password != confirm_password:
            flash("Passwords do not match", "danger")
            return redirect(url_for("student.change_password"))

        user.password = new_password
        db.session.commit()

        flash("Password updated successfully", "success")
        return redirect(url_for("student.student_dashboard"))

    return render_template("student/change_password.html")



@bp.route("/download-pdf/<int:student_id>")
@login_required(("admin", "teacher", "student"))
def download_pdf(student_id):

    student = Student.query.get_or_404(student_id)
    result = Result.query.filter_by(
        student_id=student.id
    ).first_or_404()

    pdf = generate_result_pdf(student, result)

    response = make_response(pdf)
    response.headers["Content-Disposition"] = (
        f"attachment; filename=Result_{student.roll_no}.pdf"
    )
    response.headers["Content-Type"] = "application/pdf"

    return response

@bp.route("/profile", methods=["GET", "POST"])
@login_required("student")
def profile():

    student = Student.query.filter_by(
        user_id=session["user_id"]
    ).first_or_404()

    if request.method == "POST":

        file = request.files.get("photo")

        if file and file.filename:
            student.photo = file.read()  
            db.session.commit()

        flash("Profile updated successfully", "success")
        return redirect(url_for("student.profile"))

    return render_template("student/profile.html", student=student)

@bp.route("/photo/<int:student_id>")
def student_photo(student_id):

    student = Student.query.get_or_404(student_id)

    if not student.photo:
        return "", 204  

    return Response(
        student.photo,
        mimetype="image/png"
    )