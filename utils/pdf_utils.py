import os
import pdfkit
from flask import current_app, render_template
from models import StudentMarks

def generate_result_pdf(student, result):

    marks = StudentMarks.query.filter_by(
        student_id=student.id
    ).all()

    details = [{
        "subject": m.subject.subject_name,
        "marks": m.marks,
        "max": m.subject.max_marks
    } for m in marks]

    static_path = os.path.join(
        current_app.root_path, "static"
    ).replace(os.sep, "/")

    html = render_template(
        "student/result.html",
        student=student,
        result=result,
        details=details,
        pdf_mode=True,
        static_path=static_path
    )

    # ===== PDF CONFIG =====
    config = pdfkit.configuration(
        wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
    )

    options = {
        "enable-local-file-access": "",
        "page-size": "A4",
        "orientation": "Landscape",
        "margin-top": "10mm",
        "margin-bottom": "10mm",
        "margin-left": "10mm",
        "margin-right": "10mm",
        "dpi": 300,
        "load-error-handling": "ignore",
        "load-media-error-handling": "ignore"
    }

    pdf = pdfkit.from_string(
        html,
        False,
        configuration=config,
        options=options
    )

    return pdf
