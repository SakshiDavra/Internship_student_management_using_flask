from flask import Flask,session
from config import Config
from models import db,Student
from routes import auth_bp, admin_bp, teacher_bp, student_bp
from utils.seed import seed_data
from extensions import mail

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = "super_secret_key"

db.init_app(app)
mail.init_app(app)

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(teacher_bp)
app.register_blueprint(student_bp)

with app.app_context():
    print("DB CREATE RUN")
    db.create_all()
    seed_data()


if __name__ == "__main__":
    app.run(debug=True)





