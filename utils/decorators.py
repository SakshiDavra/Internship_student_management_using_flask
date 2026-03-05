from flask import session, redirect, url_for
from functools import wraps

def login_required(roles):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):

            if "user_id" not in session:
                return redirect(url_for("auth.login"))

            if isinstance(roles, str):
                allowed_roles = (roles,)
            else:
                allowed_roles = roles

            if session.get("role") not in allowed_roles:
                role = session.get("role")

                if role == "admin":
                    return redirect(url_for("admin.admin_dashboard"))
                elif role == "teacher":
                    return redirect(url_for("teacher.teacher_dashboard"))
                elif role == "student":
                    return redirect(url_for("student.student_dashboard"))
                else:
                    return redirect(url_for("auth.login"))

            return func(*args, **kwargs)
        return wrapper
    return decorator
