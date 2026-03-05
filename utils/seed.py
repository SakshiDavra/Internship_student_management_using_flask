from models import db, Role, User

def seed_data():

    if not Role.query.first():
        for r in ["admin", "teacher", "student"]:
            db.session.add(Role(role_name=r))
        db.session.commit()

    admin_role = Role.query.filter_by(role_name="admin").first()
    if admin_role and not User.query.filter_by(username="admin").first():
        db.session.add(User(
            username="admin",
            password="admin123",
            role_id=admin_role.id
        ))
        db.session.commit()

