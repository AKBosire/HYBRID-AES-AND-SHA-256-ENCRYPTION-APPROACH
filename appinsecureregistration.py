import os
import random
import sqlite3
import smtplib
from flask import Flask, render_template, request, redirect, url_for, flash, session
from email.mime.text import MIMEText
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Allow profile picture uploads
UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Try-decode helper for viewing DB contents
def try_decode(val):
    if isinstance(val, bytes):
        return val.decode('utf-8', errors='replace')
    return val

app.jinja_env.filters['try_decode'] = try_decode

# Connect SQLite and create table if not exists
conn = sqlite3.connect('employees.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        login_email TEXT,
        email TEXT,
        password TEXT,
        dob TEXT,
        position TEXT,
        salary TEXT,
        phone TEXT,
        address TEXT,
        department TEXT,
        hire_date TEXT,
        emergency_contact TEXT,
        profile_picture TEXT,
        country TEXT,
        bio TEXT,
        linkedin TEXT,
        twitter TEXT
    )
''')
conn.commit()

# Helper: file type check
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Email verification (demo only)
def send_email_verification(to_email, code):
    sender_email = "thebinancedon@gmail.com"
    sender_password = "maug ibnj rjgb xdap"
    subject = "Your Verification Code"
    body = f"Your verification code is: {code}"
    
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = to_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, msg.as_string())
    except Exception as e:
        print(f"Failed to send email: {e}")

# ----------- ROUTES -----------

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        login_email = request.form['email']
        email = request.form['email']
        password = request.form['password']
        dob = request.form['dob']
        position = request.form['position']
        salary = request.form['salary']
        phone = request.form['phone']
        address = request.form['address']
        department = request.form['department']
        hire_date = request.form['hire_date']
        emergency_contact = request.form['emergency_contact']
        country = request.form['country']
        bio = request.form.get('bio', '')
        linkedin = request.form.get('linkedin', '')
        twitter = request.form.get('twitter', '')

        profile_picture = None
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_filename = f"{random.randint(1000,9999)}_{filename}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)
                profile_picture = unique_filename

        cursor.execute('''
            INSERT INTO employees (name, login_email, email, password, dob, position, salary, phone, address,
                                   department, hire_date, emergency_contact, profile_picture, country, bio,
                                   linkedin, twitter)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, login_email, email, password, dob, position, salary, phone, address,
              department, hire_date, emergency_contact, profile_picture, country, bio,
              linkedin, twitter))
        conn.commit()

        flash("Employee registered successfully!", "success")
        return redirect(url_for('index'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_email = request.form['email']
        login_password = request.form['password']
        cursor.execute("SELECT * FROM employees WHERE login_email = ?", (login_email,))
        employee = cursor.fetchone()
        if employee:
            if login_password == employee[4]:
                session['employee_id'] = employee[0]
                code = str(random.randint(100000, 999999))
                session['verification_code'] = code
                send_email_verification(login_email, code)
                flash("Verification code sent to your email!", "info")
                return redirect(url_for('validate_code'))
            else:
                flash("Incorrect password!", "danger")
        else:
            flash("Email not found!", "danger")
    return render_template('login.html')

@app.route('/validate_code', methods=['GET', 'POST'])
def validate_code():
    if request.method == 'POST':
        user_code = request.form['code']
        if user_code == session.get('verification_code'):
            flash("Verification successful!", "success")
            return redirect(url_for('employee_view'))
        else:
            flash("Invalid verification code!", "danger")
    return render_template('validate_code.html')

@app.route('/employee_view', methods=['GET'])
def employee_view():
    emp_id = session.get('employee_id')
    if not emp_id:
        flash("Please log in first.", "danger")
        return redirect(url_for('login'))

    cursor.execute("SELECT * FROM employees WHERE id = ?", (emp_id,))
    row = cursor.fetchone()
    if row:
        employee = {
            "name": row[1], "email": row[3], "dob": row[5],
            "position": row[6], "salary": row[7], "phone": row[8],
            "address": row[9], "department": row[10], "hire_date": row[11],
            "emergency_contact": row[12], "profile_picture": row[13],
            "country": row[14], "bio": row[15],
            "linkedin": row[16], "twitter": row[17]
        }
        return render_template('view.html', **employee)
    else:
        flash("Employee not found", "danger")
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)  # HTTP mode for Wireshark plaintext capture
