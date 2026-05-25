import os
import random
import sqlite3
import smtplib
from flask import Flask, render_template, request, redirect, url_for, flash, session
from email.mime.text import MIMEText
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # In production, use an environment variable

# Register a try_decode filter that decodes bytes if needed, or returns the value as-is.
def try_decode(val):
    if isinstance(val, bytes):
        return val.decode('utf-8', errors='replace')
    return val

app.jinja_env.filters['try_decode'] = try_decode

# Configure file uploads
UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Connect to SQLite database and create the employees table.
# All fields are stored in plaintext.
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

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Admin password for admin routes (stored in plaintext)
ADMIN_PASSWORD = "admin123"  # Change this in production!

def send_email_verification(to_email, code):
    sender_email = "thebinancedon@gmail.com"      # Replace with your email
    sender_password = "maug ibnj rjgb xdap"        # Replace with your email password (or use environment variables)
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

# -------------------- Routes --------------------

@app.route('/')
def index():
    return render_template('index.html')

# ----- Employee Registration -----
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        login_email = request.form['email']   # For login lookup
        email = request.form['email']          # Stored as plaintext
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
            INSERT INTO employees (name, login_email, email, password, dob, position, salary, phone, address, department,
                                   hire_date, emergency_contact, profile_picture, country, bio, linkedin, twitter)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, login_email, email, password, dob, position, salary,
              phone, address, department, hire_date, emergency_contact,
              profile_picture, country, bio, linkedin, twitter))
        conn.commit()
        
        flash("Employee registered successfully!", "success")
        return redirect(url_for('index'))
    
    return render_template('register.html')

# ----- Employee Login -----
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_email = request.form['email']
        login_password = request.form['password']
        cursor.execute("SELECT * FROM employees WHERE login_email = ?", (login_email,))
        employee = cursor.fetchone()
        if employee:
            stored_password = employee[4]  # password column index
            if login_password == stored_password:
                session['employee_id'] = employee[0]
                verification_code = str(random.randint(100000, 999999))
                session['verification_code'] = verification_code
                send_email_verification(login_email, verification_code)
                flash("Verification code sent to your email!", "info")
                return redirect(url_for('validate_code'))
            else:
                flash("Incorrect password!", "danger")
        else:
            flash("Email not found!", "danger")
    return render_template('login.html')

# ----- Verification Code for Employee Login -----
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

# ----- Employee View (after successful login verification) -----
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
            "name": row[1],
            "email": row[3],
            "dob": row[5],
            "position": row[6],
            "salary": row[7],
            "phone": row[8],
            "address": row[9],
            "department": row[10],
            "hire_date": row[11],
            "emergency_contact": row[12],
            "profile_picture": row[13],
            "country": row[14],
            "bio": row[15],
            "linkedin": row[16],
            "twitter": row[17],
        }
        return render_template('view.html', **employee)
    else:
        flash("Employee record not found.", "danger")
        return redirect(url_for('login'))

# ----- Admin Dashboard & Authentication -----
@app.route('/admin', methods=['GET'])
def admin_dashboard():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    cursor.execute("SELECT name, email, salary FROM employees")
    employees = cursor.fetchall()
    employees_list = []
    for emp in employees:
        employees_list.append({
            "name": emp[0],
            "email": emp[1],
            "salary": emp[2],
        })
    return render_template('admin_dashboard.html', employees=employees_list)

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form['password']
        if password == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Incorrect admin password!", "danger")
    return render_template('admin_login.html')

@app.route('/admin-logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('admin_login'))

# ----- /database Route to Display Raw Database Contents -----
@app.route('/database', methods=['GET'])
def database_view():
    cursor.execute("SELECT * FROM employees")
    rows = cursor.fetchall()
    columns = [description[0] for description in cursor.description]
    # Remove the 'login_email' column from display
    if "login_email" in columns:
        index = columns.index("login_email")
        columns.pop(index)
        new_rows = []
        for row in rows:
            row_list = list(row)
            row_list.pop(index)
            new_rows.append(tuple(row_list))
        rows = new_rows
    return render_template('database.html', columns=columns, rows=rows)

if __name__ == '__main__':
    app.run(debug=True)
