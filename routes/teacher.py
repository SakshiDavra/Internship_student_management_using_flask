from collections import defaultdict
from flask import Blueprint, render_template, request, redirect, url_for, session
from models import (
    db,
    Student,
    SubjectMaster,
    StudentMarks,
    TeacherAssignment,
    AcademicYear,
    Division,User
)
from utils.decorators import login_required
from utils.result_utils import calculate_result

bp = Blueprint("teacher", __name__, url_prefix="/teacher")

@bp.route("/dashboard")
@login_required("teacher")
def teacher_dashboard():

    teacher_id = session["user_id"]

    teacher = User.query.get(teacher_id)

    assignments = TeacherAssignment.query.filter_by(
        teacher_id=teacher_id
    ).all()

    class_data = []

    for a in assignments:
        students = Student.query.filter_by(
            course_id=a.course_id,
            year_id=a.year_id,
            division_id=a.division_id
        ).order_by(Student.roll_no).all()

        class_data.append({
            "assignment": a,
            "students": students
        })

    return render_template(
        "teacher/dashboard.html",
        teacher=teacher,     
        class_data=class_data
    )

@bp.route("/add-marks", methods=["GET", "POST"])
@login_required("teacher")
def add_marks():

    teacher_id = session["user_id"]

    assignments = TeacherAssignment.query.filter_by(
        teacher_id=teacher_id
    ).all()

    if not assignments:
        return render_template(
            "admin/add_marks.html",
            years=[], divisions=[], students=[], subjects=[],
            student_marks={}, edit_record=None
        )

    year_ids     = list({a.year_id for a in assignments})
    division_ids = list({a.division_id for a in assignments})
    subject_ids  = list({a.subject_id for a in assignments})

    edit_id = request.args.get("edit", type=int)
    edit_record = StudentMarks.query.get(edit_id) if edit_id else None
    #subject jo assign nathi to error
    if edit_record and edit_record.subject_id not in subject_ids:
        abort(403)

    if request.method == "POST":
        student_id = request.form.get("student_id", type=int)
        subject_id = request.form.get("subject_id", type=int)
        marks      = request.form.get("marks", type=int)

        if subject_id not in subject_ids:
            abort(403)

        record = StudentMarks.query.filter_by(
            student_id=student_id,
            subject_id=subject_id
        ).first()

        if record:
            record.marks = marks
        else:
            db.session.add(StudentMarks(
                student_id=student_id,
                subject_id=subject_id,
                marks=marks
            ))

        db.session.commit()
        calculate_result(student_id)

        return redirect(url_for("teacher.add_marks"))

    student_marks = defaultdict(list)

    marks = StudentMarks.query.join(Student).filter(
        Student.year_id.in_(year_ids),
        Student.division_id.in_(division_ids),
        StudentMarks.subject_id.in_(subject_ids)
    ).all()

    for m in marks:
        student_marks[m.student].append(m)

    return render_template(
        "admin/add_marks.html",
        years=AcademicYear.query.filter(AcademicYear.id.in_(year_ids)).all(),
        divisions=Division.query.filter(Division.id.in_(division_ids)).all(),
        students=Student.query.filter(
            Student.year_id.in_(year_ids),
            Student.division_id.in_(division_ids)
        ).order_by(Student.roll_no).all(),
        subjects=SubjectMaster.query.filter(
            SubjectMaster.id.in_(subject_ids)
        ).all(),
        student_marks=student_marks,
        edit_record=edit_record
    )

@bp.route("/get-years")
@login_required("teacher")
def get_years():
    years = (
        db.session.query(AcademicYear)
        .join(TeacherAssignment, TeacherAssignment.year_id == AcademicYear.id)
        .filter(TeacherAssignment.teacher_id == session["user_id"])
        .distinct()
        .all()
    )

    return {
        "years": [
            {"id": y.id, "name": f"{y.course.course_name} - Year {y.year_no}"}
            for y in years
        ]
    }

@bp.route("/get-students")
@login_required("teacher")
def get_students():
    year_id = request.args.get("year_id", type=int)
    division_id = request.args.get("division_id", type=int)

    students = Student.query.filter_by(
        year_id=year_id,
        division_id=division_id
    ).order_by(Student.roll_no).all()

    return {
        "students": [
            {"id": s.id, "name": f"{s.roll_no} - {s.name}"}
            for s in students
        ]
    }

@bp.route("/get-subjects")
@login_required("teacher")
def get_subjects():
    year_id     = request.args.get("year_id", type=int)
    division_id = request.args.get("division_id", type=int)

    subjects = (
        db.session.query(SubjectMaster)
        .join(TeacherAssignment, TeacherAssignment.subject_id == SubjectMaster.id)
        .filter(
            TeacherAssignment.teacher_id == session["user_id"],
            TeacherAssignment.year_id == year_id,
            TeacherAssignment.division_id == division_id
        )
        .distinct()
        .all()
    )

    return {
        "subjects": [
            {"id": s.id, "name": s.subject_name}
            for s in subjects
        ]
    }


