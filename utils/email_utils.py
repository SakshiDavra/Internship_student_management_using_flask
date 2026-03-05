from flask_mail import Message
from datetime import datetime
from models import db
from utils.pdf_utils import generate_result_pdf

def send_result_email(student, result, mail):

    print("📧 EMAIL FUNCTION CALLED")

    try:
       
        pdf = generate_result_pdf(student, result)

        msg = Message(
            subject="Your Examination Result",
            recipients=[student.user.username]
        )

        msg.body = f"""
            Hello {student.name},

            Your examination result has been published.

            Roll No     : {student.roll_no}
            Percentage  : {result.percentage:.2f} %
            Grade       : {result.grade}

            Please find attached your official result PDF.

            Regards,
            Catalyst Academy
            """

        msg.attach(
            filename=f"Result_{student.roll_no}.pdf",
            content_type="application/pdf",
            data=pdf
        )

        mail.send(msg)
        result.email_status = "SUCCESS"
        result.email_error = None
        result.email_sent_count = (result.email_sent_count or 0) + 1
        result.last_email_sent_at = datetime.utcnow()
        db.session.commit()

        print("EMAIL SENT")
        return True

    except Exception as e:
        db.session.rollback()

        msg = str(e).lower()

        if "invalid" in msg or "recipient" in msg:
            short_error = "Invalid student email address"
        elif "connection" in msg or "timed out" in msg:
            short_error = "Email server not responding"
        elif "authentication" in msg or "login" in msg:
            short_error = "Email authentication failed"
        elif "refused" in msg or "rejected" in msg:
            short_error = "Email rejected by server"
        else:
            short_error = "Email sending failed"

        result.email_status = "FAILED"
        result.email_error = short_error
        result.last_email_sent_at = datetime.utcnow()
        db.session.commit()

        print("EMAIL FAILED:", short_error)
        return False
