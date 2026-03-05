from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Role(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(20), unique=True, nullable=False)

    users = db.relationship("User", backref="role", cascade="all, delete")

# ================= USER =================
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    role_id = db.Column(
        db.Integer,
        db.ForeignKey("roles.id", ondelete="CASCADE"),
        nullable=False
    )

    student = db.relationship(
        "Student", backref="user", uselist=False, cascade="all, delete"
    )


# ================= COURSE =================
class Course(db.Model):
    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(50), nullable=False)  
    duration_years = db.Column(db.Integer, nullable=False) 

    years = db.relationship("AcademicYear", backref="course", cascade="all, delete")


# ================= ACADEMIC YEAR =================
class AcademicYear(db.Model):
    __tablename__ = "academic_years"

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(
        db.Integer,
        db.ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False
    )

    year_no = db.Column(db.Integer, nullable=False) 
    is_active = db.Column(db.Boolean, default=True)


# ================= DIVISION =================
class Division(db.Model):
    __tablename__ = "divisions"

    id = db.Column(db.Integer, primary_key=True)
    division_name = db.Column(db.String(5), nullable=False)  


# ================= STUDENT =================
class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    roll_no = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)

    course_id = db.Column(
        db.Integer,
        db.ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False
    )

    year_id = db.Column(
        db.Integer,
        db.ForeignKey("academic_years.id", ondelete="CASCADE"),
        nullable=False
    )

    division_id = db.Column(
        db.Integer,
        db.ForeignKey("divisions.id", ondelete="CASCADE"),
        nullable=False
    )

    photo = db.Column(db.LargeBinary, nullable=True)


    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )

    marks = db.relationship(
        "StudentMarks", backref="student", cascade="all, delete"
    )

    result = db.relationship(
        "Result", backref="student", uselist=False, cascade="all, delete"
    )

    course = db.relationship("Course")
    year = db.relationship("AcademicYear")
    division = db.relationship("Division")

class SubjectMaster(db.Model):
    __tablename__ = "subject_master"

    id = db.Column(db.Integer, primary_key=True)
    subject_name = db.Column(db.String(100), nullable=False)
    max_marks = db.Column(db.Integer, nullable=False)

    course_id = db.Column(
        db.Integer,
        db.ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False
    )

    year_id = db.Column(
        db.Integer,
        db.ForeignKey("academic_years.id", ondelete="CASCADE"),
        nullable=False
    )

    course = db.relationship("Course", backref="subjects")
    year = db.relationship("AcademicYear", backref="subjects")

class TeacherAssignment(db.Model):
    __tablename__ = "teacher_assignments"

    id = db.Column(db.Integer, primary_key=True)

    teacher_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    course_id = db.Column(
        db.Integer,
        db.ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False
    )

    year_id = db.Column(
        db.Integer,
        db.ForeignKey("academic_years.id", ondelete="CASCADE"),
        nullable=False
    )

    division_id = db.Column(
        db.Integer,
        db.ForeignKey("divisions.id", ondelete="CASCADE"),
        nullable=False
    )

    subject_id = db.Column(
        db.Integer,
        db.ForeignKey("subject_master.id", ondelete="CASCADE"),
        nullable=False
    )

    teacher = db.relationship("User")
    course = db.relationship("Course")
    year = db.relationship("AcademicYear")
    division = db.relationship("Division")
    subject = db.relationship("SubjectMaster")

    __table_args__ = (
        db.UniqueConstraint(
            "teacher_id",
            "course_id",
            "year_id",
            "division_id",
            "subject_id"
        ),
    )

class StudentMarks(db.Model):
    __tablename__ = "student_marks"

    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False
    )

    subject_id = db.Column(
        db.Integer,
        db.ForeignKey("subject_master.id", ondelete="CASCADE"),
        nullable=False
    )

    marks = db.Column(db.Integer, nullable=False)

    subject = db.relationship("SubjectMaster")

    __table_args__ = (
        db.UniqueConstraint("student_id", "subject_id"),
    )

class Result(db.Model):
    __tablename__ = "results"

    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False
    )

    total_marks = db.Column(db.Integer)
    percentage = db.Column(db.Float)
    grade = db.Column(db.String(5))
    is_published = db.Column(db.Boolean, default=False)
    email_status = db.Column(db.String(20))  
    email_error = db.Column(db.Text, nullable=True)
    email_sent_count = db.Column(db.Integer, default=0)
    last_email_sent_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
