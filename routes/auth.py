from flask import Blueprint, render_template, request, redirect, url_for, session
from models import User

bp = Blueprint("auth", __name__)

@bp.route("/")
def index():
    if "user_id" in session:
        role = session.get("role")

        if role == "admin":
            return redirect(url_for("admin.admin_dashboard"))
        elif role == "teacher":
            return redirect(url_for("teacher.teacher_dashboard"))
        else:
            return redirect(url_for("student.student_dashboard"))

    return redirect(url_for("auth.login"))

@bp.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("auth.index"))

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session["user_id"] = user.id
            session["role"] = user.role.role_name
            return redirect(url_for("auth.index"))

    return render_template("auth/login.html")

@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
