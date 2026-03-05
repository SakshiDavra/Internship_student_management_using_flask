# 🎓 Flask Student Management System

A web-based **Student Management System** built using the **Flask framework**.
This system helps educational institutes manage student records, marks, and results efficiently with role-based access for Admin and Teachers.

---

✨ Key Features

👨‍💼 Admin Panel

* Manage all students in the system
* Manage teacher accounts
* Publish student results
* Send result notifications via email
* Monitor and manage the entire system

👩‍🏫 Teacher Panel

* Manage only their assigned students
* Add and update student marks
* Edit marks when required
* Teachers cannot view or modify students assigned to other teachers

🎓 Student Features

* Students can view only their own records
* Check and download their results

📄 Result Management

* Generate downloadable result PDF using **wkhtml2pdf**
* Students can download their results easily

📧 Email Notification

* Automatic email sent to students when results are published

🔐 Authentication & Security

* Secure login system
* Forgot password functionality
* Role-based access control
* Teachers can access only their own data

---

🛠 Tech Stack

* **Backend:** Python, Flask
* **Frontend:** HTML, CSS, Bootstrap
* **Template Engine:** Jinja2
* **PDF Generation:** wkhtml2pdf
* **Email Service:** SMTP
* **Database:** SQLite / MySQL
* **Version Control:** Git & GitHub

---

👩‍💻 Author

**Sakshi Davra**
