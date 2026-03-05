from flask import Blueprint, render_template, request, redirect, url_for,session,flash
from models import  db, Role, User, Student, SubjectMaster, StudentMarks,Course, AcademicYear, Division, TeacherAssignment,Result
from utils.decorators import login_required
from utils.result_utils import calculate_result
from collections import defaultdict
from utils.email_utils import send_result_email
from extensions import mail


bp = Blueprint("admin", __name__, url_prefix="/admin")

@bp.route("/dashboard")
@login_required("admin")
def admin_dashboard():
    students = Student.query.order_by(Student.roll_no).all()
    teachers = User.query.join(Role).filter(Role.role_name == "teacher").all()
    return render_template(
        "admin/dashboard.html",
        students=students,
        teachers=teachers
    )


@bp.route("/add-student", methods=["GET", "POST"])
@login_required("admin")
def add_student():

    courses = Course.query.all()
    years = AcademicYear.query.all()
    divisions = Division.query.all()

    student_id = request.args.get("id", type=int)
    student = Student.query.get(student_id) if student_id else None

    if request.method == "POST":

        # EDIT
        if student:
            student.roll_no = request.form["roll_no"]
            student.name = request.form["name"]
            student.course_id = request.form["course_id"]
            student.year_id = request.form["year_id"]
            student.division_id = request.form["division_id"]
            db.session.commit()
            return redirect(url_for("admin.admin_dashboard"))

        # ADD
        role = Role.query.filter_by(role_name="student").first()

        user = User(
            username=request.form["username"],
            password="student",
            role_id=role.id
        )
        db.session.add(user)
        db.session.commit()

        student = Student(
            roll_no=request.form["roll_no"],
            name=request.form["name"],
            course_id=request.form["course_id"],
            year_id=request.form["year_id"],
            division_id=request.form["division_id"],
            user_id=user.id
        )
        db.session.add(student)
        db.session.commit()
        return redirect(url_for("admin.admin_dashboard"))

    return render_template(
        "admin/add_student.html",
        courses=courses,
        years=years,
        divisions=divisions,
        student=student
    )

@bp.route("/add-teacher", methods=["GET", "POST"])
@login_required("admin")
def add_teacher():

    teacher_id = request.args.get("id", type=int)
    teacher = User.query.get(teacher_id) if teacher_id else None

    if request.method == "POST":

        # EDIT
        if teacher:
            teacher.username = request.form["username"]
            db.session.commit()
            return redirect(url_for("admin.admin_dashboard"))

        # ADD
        role = Role.query.filter_by(role_name="teacher").first()
        user = User(
            username=request.form["username"],
            password="teacher",
            role_id=role.id
        )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("admin.admin_dashboard"))

    return render_template("admin/add_teacher.html", teacher=teacher)

@bp.route("/delete-student/<int:id>")
@login_required("admin")
def delete_student(id):
    db.session.delete(Student.query.get_or_404(id))
    db.session.commit()
    return redirect(url_for("admin.admin_dashboard"))


@bp.route("/delete-teacher/<int:id>")
@login_required("admin")
def delete_teacher(id):
    db.session.delete(User.query.get_or_404(id))
    db.session.commit()
    return redirect(url_for("admin.admin_dashboard"))

@bp.route("/subjects", methods=["GET", "POST"])
@login_required("admin")
def manage_subjects():

    courses = Course.query.all()
    years = AcademicYear.query.all()

    if request.method == "POST":
        exists = SubjectMaster.query.filter_by(
            subject_name=request.form["subject_name"],
            course_id=request.form["course_id"],
            year_id=request.form["year_id"]
        ).first()

        if not exists:
            db.session.add(SubjectMaster(
                subject_name=request.form["subject_name"],
                max_marks=request.form["max_marks"],
                course_id=request.form["course_id"],
                year_id=request.form["year_id"]
            ))
            db.session.commit()

        return redirect(url_for("admin.manage_subjects"))

    subjects = SubjectMaster.query.all()
    return render_template(
        "admin/subjects.html",
        subjects=subjects,
        courses=courses,
        years=years
    )

@bp.route("/add-marks", methods=["GET", "POST"])
@login_required(("admin", "teacher"))
def add_marks():

    edit_id = request.args.get("edit", type=int)
    edit_record = StudentMarks.query.get(edit_id) if edit_id else None

    if request.method == "POST":

        mark_id   = request.form.get("mark_id", type=int)
        student_id = request.form.get("student_id", type=int)
        subject_id = request.form.get("subject_id", type=int)
        marks      = request.form.get("marks", type=int)

        # Edit
        if mark_id:
            record = StudentMarks.query.get_or_404(mark_id)
            record.marks = marks
            student_id = record.student_id

        # ADD
        else:
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

        return redirect(url_for("admin.add_marks"))

    years     = AcademicYear.query.all()
    divisions = Division.query.all()

    student_marks = defaultdict(list)
    for m in StudentMarks.query.all():
        student_marks[m.student].append(m)

    return render_template(
        "admin/add_marks.html",
        years=years,
        divisions=divisions,
        student_marks=student_marks,
        edit_record=edit_record
    )

@bp.route("/courses", methods=["GET", "POST"])
@login_required("admin")
def manage_courses():

    if request.method == "POST":
        db.session.add(Course(
            course_name=request.form["course_name"],
            duration_years=request.form["duration"]
        ))
        db.session.commit()
        return redirect(url_for("admin.manage_courses"))

    return render_template("admin/courses.html", courses=Course.query.all())

@bp.route("/academic-years", methods=["GET", "POST"])
@login_required("admin")
def manage_years():

    if request.method == "POST":
        course_id = request.form.get("course_id", type=int)
        year_no   = request.form.get("year_no", type=int)
        exists = AcademicYear.query.filter_by(
            course_id=course_id,
            year_no=year_no
        ).first()

        if not exists:
            db.session.add(AcademicYear(
                course_id=course_id,
                year_no=year_no
            ))
            db.session.commit()

        return redirect(url_for("admin.manage_years"))

    courses = Course.query.all()

    return render_template(
        "admin/academic_years.html",
        courses=courses
    )
    
@bp.route("/divisions", methods=["GET", "POST"])
@login_required("admin")
def manage_divisions():

    if request.method == "POST":
        db.session.add(Division(
            division_name=request.form["division"]
        ))
        db.session.commit()
        return redirect(url_for("admin.manage_divisions"))

    return render_template(
        "admin/divisions.html",
        divisions=Division.query.all()
    )

@bp.route("/assign-teacher", methods=["GET", "POST"])
@login_required("admin")
def assign_teacher():

    teachers = User.query.join(Role).filter(Role.role_name == "teacher").all()

    if request.method == "POST":
        db.session.add(TeacherAssignment(
            teacher_id=request.form["teacher_id"],
            course_id=request.form["course_id"],
            year_id=request.form["year_id"],
            division_id=request.form["division_id"],
            subject_id=request.form["subject_id"]
        ))
        db.session.commit()
        return redirect(url_for("admin.assign_teacher"))

    return render_template(
        "admin/assign_teacher.html",
        teachers=teachers,
        courses=Course.query.all(),
        years=AcademicYear.query.all(),
        divisions=Division.query.all(),
        subjects=SubjectMaster.query.all(),
        assignments=TeacherAssignment.query.all()
    )
@bp.route("/delete-marks/<int:id>")
@login_required("admin")
def delete_marks(id):
    record = StudentMarks.query.get_or_404(id)
    student_id = record.student_id

    db.session.delete(record)
    db.session.commit()

    calculate_result(student_id)
    return redirect(url_for("admin.add_marks"))


#assign teacher na marks nu

@bp.route("/get-years/<int:course_id>")
@login_required("admin")
def get_years(course_id):
    years = AcademicYear.query.filter_by(course_id=course_id).all()
    return {
        "years": [
            {"id": y.id, "name": f"Year {y.year_no}"}
            for y in years
        ]
    }

@bp.route("/get-subjects")
@login_required("admin")
def get_subjects():
    course_id = request.args.get("course_id", type=int)
    year_id   = request.args.get("year_id", type=int)

    subjects = SubjectMaster.query.filter_by(
        course_id=course_id,
        year_id=year_id
    ).all()

    return {
        "subjects": [
            {"id": s.id, "name": s.subject_name}
            for s in subjects
        ]
    }
@bp.route("/view-result/<int:student_id>")
@login_required(("admin", "teacher", "student"))
def view_result(student_id):

    role = session.get("role")
    user_id = session.get("user_id")

    if role == "student":
        student = Student.query.filter_by(user_id=user_id).first_or_404()
        if student.id != student_id:
            abort(403)

    elif role == "teacher":
        student = Student.query.get_or_404(student_id)
        allowed = TeacherAssignment.query.filter_by(
            teacher_id=user_id,
            course_id=student.course_id,
            year_id=student.year_id,
            division_id=student.division_id
        ).first()
        if not allowed:
            abort(403)

    else:  # admin
        student = Student.query.get_or_404(student_id)

    marks = StudentMarks.query.filter_by(student_id=student.id).all()

    details = [{
        "subject": m.subject.subject_name,
        "marks": m.marks,
        "max": m.subject.max_marks
    } for m in marks]

    if role == "student":
        result = Result.query.filter_by(
            student_id=student.id,
            is_published=True
        ).first()
    else:
        result = Result.query.filter_by(
            student_id=student.id
        ).first()

    return render_template(
        "student/result.html",
        student=student,
        result=result,
        details=details,
        is_pdf=False
    )

@bp.route("/get-students")
@login_required(("admin"))
def get_students():
    year_id = request.args.get("year_id", type=int)
    division_id = request.args.get("division_id", type=int)

    students = Student.query.filter_by(
        year_id=year_id,
        division_id=division_id
    ).order_by(Student.roll_no).all()

    return {
        "students": [
            {
                "id": s.id,
                "roll_no": s.roll_no,
                "name": s.name
            }
            for s in students
        ]
    }

@bp.route("/get-subjects-by-year")
@login_required(("admin"))
def get_subjects_by_year():
    year_id = request.args.get("year_id", type=int)

    subjects = SubjectMaster.query.filter_by(
        year_id=year_id
    ).all()

    return {
        "subjects": [
            {"id": s.id, "name": s.subject_name}
            for s in subjects
        ]
    }

@bp.route("/publish-result/<int:student_id>")
@login_required("admin")
def publish_result(student_id):

    result = Result.query.filter_by(student_id=student_id).first_or_404()
    student = Student.query.get_or_404(student_id)

    if result.is_published:
        flash("Result already published", "info")
        return redirect(url_for("admin.admin_dashboard"))

    try:
        send_result_email(student, result, mail)

        result.is_published = True
        db.session.commit()

        flash("Result published & email sent", "success")

    except Exception:
        flash("Email failed. Result NOT published.", "danger")

    return redirect(url_for("admin.admin_dashboard"))

@bp.route("/publish-selected-results", methods=["POST"])
@login_required("admin")
def publish_selected_results():

    student_ids = request.form.getlist("student_ids")

    if not student_ids:
        flash("No students selected", "warning")
        return redirect(url_for("admin.admin_dashboard"))

    results = Result.query.filter(
        Result.student_id.in_(student_ids)
    ).all()

    to_email = []
    for r in results:
        if not r.is_published:
            r.is_published = True
            to_email.append(r)

    db.session.commit()

    sent = 0
    for r in to_email:
        student = Student.query.get(r.student_id)
        try:
            send_result_email(student, r, mail)
            sent += 1
        except Exception as e:
            print("EMAIL ERROR:", e)

    flash(f"{sent} results published & emailed successfully", "success")
    return redirect(url_for("admin.admin_dashboard"))

@bp.route("/unpublish-result/<int:student_id>")
@login_required("admin")
def unpublish_result(student_id):

    result = Result.query.filter_by(student_id=student_id).first_or_404()
    result.is_published = False
    db.session.commit()

    return redirect(url_for("admin.admin_dashboard"))
    
@bp.route("/resend-result-email/<int:student_id>")
@login_required("admin")
def resend_result_email(student_id):

    result = Result.query.filter_by(student_id=student_id).first_or_404()
    student = Student.query.get_or_404(student_id)

    try:
        send_result_email(student, result, mail)
        flash("Email resent successfully", "success")
    except Exception:
        flash("Email failed again", "danger")

    return redirect(url_for("admin.admin_dashboard"))
