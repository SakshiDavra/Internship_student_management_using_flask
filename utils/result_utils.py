from models import db, StudentMarks, SubjectMaster, Result

def calculate_result(student_id):
    marks = StudentMarks.query.filter_by(student_id=student_id).all()

    total = 0
    max_total = 0

    for m in marks:
        total += m.marks
        max_total += m.subject.max_marks

    percentage = (total / max_total * 100) if max_total else 0

    if percentage >= 90:
        grade = "A+"
    elif percentage >= 80:
        grade = "A"
    elif percentage >= 70:
        grade = "B+"
    elif percentage >= 60:
        grade = "B"
    elif percentage >= 50:
        grade = "c"
    else:
        grade = "D"
    result = Result.query.filter_by(student_id=student_id).first()
    if not result:
        result = Result(student_id=student_id)

    result.total_marks = total
    result.percentage = percentage
    result.grade = grade

    db.session.add(result)
    db.session.commit()
