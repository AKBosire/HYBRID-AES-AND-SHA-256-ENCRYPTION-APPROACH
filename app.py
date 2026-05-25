import os
import random
import sqlite3
import smtplib
import hashlib
import json
import time
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session
from email.mime.text import MIMEText
from werkzeug.utils import secure_filename
from cryptography.fernet import Fernet
import plotly.graph_objects as go
import plotly.io as pio

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# ====================== TLS CONFIGURATION ======================
def run_with_tls():
    cert_file = 'cert.pem'
    key_file = 'key.pem'
    
    if os.path.exists(cert_file) and os.path.exists(key_file):
        print("=" * 100)
        print("🚀 EMPLOYEE DATA ENCRYPTION SYSTEM - PROFESSIONAL TLS ENABLED")
        print("Main Login Page     → https://127.0.0.1:5000")
        print("DDoS Dashboard      → https://127.0.0.1:5000/ddos_dashboard")
        print("Admin Encrypted     → https://127.0.0.1:5000/admin/encrypted")
        print("Admin Decrypted     → https://127.0.0.1:5000/admin/decrypted")
        print("=" * 100)
        print("🔧 WIRESHARK FILTERS:")
        print("   tcp.port == 5000                    → Full Traffic")
        print("   tcp.port == 5000 && tls             → TLS Traffic (Recommended)")
        print("   tcp.port == 5000 && tls.handshake   → TLS Handshake Only")
        print("   tcp.port == 5000 && tls.app_data    → Encrypted Application Data")
        print("=" * 100)
        print("Tip: Start with tcp.port == 5000, then right-click → Decode As → TLS")
        print("=" * 100)
        
        app.run(
            host='127.0.0.1',
            port=5000,
            ssl_context=(cert_file, key_file),
            debug=True,
            threaded=True,
            use_reloader=False
        )
    else:
        print("❌ cert.pem or key.pem not found!")
        print("Generate them with: openssl req -x509 -newkey rsa:2048 -nodes -keyout key.pem -out cert.pem -days 365 -subj \"/C=KE/ST=Nairobi/L=Nairobi/O=Kefa/CN=127.0.0.1\"")
        print("Falling back to adhoc...")
        app.run(host='127.0.0.1', port=5000, ssl_context='adhoc', debug=True, threaded=True, use_reloader=False)

# Load AES key
with open("aes_secret.key", "rb") as f:
    key = f.read()
fernet = Fernet(key)

# Email alert settings
ALERT_EMAIL = "bosirekefa@gmail.com"
last_alert_time = 0

# Encryption and hashing functions
def encrypt(data):
    return fernet.encrypt(data.encode()).decode() if data else None

def decrypt(data):
    return fernet.decrypt(data.encode()).decode() if data else None

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def send_intruder_alert(intensity):
    global last_alert_time
    current_time = time.time()
    if current_time - last_alert_time < 60:
        return
    last_alert_time = current_time

    sender_email = "thebinancedon@gmail.com"
    sender_password = "maug ibnj rjgb xdap"
    subject = "🚨 INTRUDER ALERT - DDoS Attack Detected"
    body = f"""Alert: Intruder trying to hack the system thru DDoS.

Current Attack Intensity: {intensity}%
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

System is under heavy simulated attack on port 5000."""

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = ALERT_EMAIL

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, ALERT_EMAIL, msg.as_string())
        print(f"✅ Intruder alert sent (Intensity: {intensity}%)")
    except Exception as e:
        print(f"Failed to send alert: {e}")

UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# SQLite connection
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

# ====================== MAIN ROUTES ======================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = encrypt(request.form['name'])
        login_email = request.form['email']
        email = encrypt(request.form['email'])
        password = hash_password(request.form['password'])
        dob = encrypt(request.form['dob'])
        position = encrypt(request.form['position'])
        salary = encrypt(request.form['salary'])
        phone = encrypt(request.form['phone'])
        address = encrypt(request.form['address'])
        department = encrypt(request.form['department'])
        hire_date = encrypt(request.form['hire_date'])
        emergency_contact = encrypt(request.form['emergency_contact'])
        country = encrypt(request.form['country'])
        bio = encrypt(request.form.get('bio', ''))
        linkedin = encrypt(request.form.get('linkedin', ''))
        twitter = encrypt(request.form.get('twitter', ''))

        profile_picture = None
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_filename = f"{random.randint(1000,9999)}_{filename}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)
                profile_picture = encrypt(unique_filename)

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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_email = request.form['email']
        login_password = request.form['password']
        cursor.execute("SELECT * FROM employees WHERE login_email = ?", (login_email,))
        employee = cursor.fetchone()
        if employee and hash_password(login_password) == employee[4]:
            session['employee_id'] = employee[0]
            code = str(random.randint(100000, 999999))
            session['verification_code'] = code
            send_email_verification(login_email, code)
            flash("Verification code sent to your email!", "info")
            return redirect(url_for('validate_code'))
        else:
            flash("Invalid login credentials.", "danger")
    return render_template('login.html')

@app.route('/validate_code', methods=['GET', 'POST'])
def validate_code():
    if request.method == 'POST':
        if request.form['code'] == session.get('verification_code'):
            flash("Verification successful!", "success")
            return redirect(url_for('employee_view'))
        else:
            flash("Invalid verification code!", "danger")
    return render_template('validate_code.html')

@app.route('/employee_view')
def employee_view():
    emp_id = session.get('employee_id')
    if not emp_id:
        flash("Please log in first.", "danger")
        return redirect(url_for('login'))

    cursor.execute("SELECT * FROM employees WHERE id = ?", (emp_id,))
    row = cursor.fetchone()
    if row:
        employee = {
            "name": decrypt(row[1]),
            "email": decrypt(row[3]),
            "dob": decrypt(row[5]),
            "position": decrypt(row[6]),
            "salary": decrypt(row[7]),
            "phone": decrypt(row[8]),
            "address": decrypt(row[9]),
            "department": decrypt(row[10]),
            "hire_date": decrypt(row[11]),
            "emergency_contact": decrypt(row[12]),
            "profile_picture": decrypt(row[13]) if row[13] else None,
            "country": decrypt(row[14]),
            "bio": decrypt(row[15]),
            "linkedin": decrypt(row[16]),
            "twitter": decrypt(row[17])
        }
        return render_template('view.html', **employee)
    flash("Employee not found.", "danger")
    return redirect(url_for('login'))

@app.route('/database', methods=['GET'])
def database_view():
    cursor.execute("SELECT * FROM employees")
    rows = cursor.fetchall()
    columns = [description[0] for description in cursor.description]
    return render_template('database.html', columns=columns, rows=rows)

@app.route('/admin/encrypted')
def admin_encrypted_view():
    cursor.execute("SELECT * FROM employees")
    rows = cursor.fetchall()
    columns = [description[0] for description in cursor.description]
    return render_template('admin_encrypted.html', columns=columns, rows=rows, title="Raw Encrypted Database (AES + SHA-256)")

@app.route('/admin/decrypted')
def admin_decrypted_view():
    cursor.execute("SELECT * FROM employees")
    rows = cursor.fetchall()
    columns = [description[0] for description in cursor.description]
    
    decrypted_rows = []
    for row in rows:
        decrypted_rows.append({
            "id": row[0],
            "name": decrypt(row[1]) or "N/A",
            "login_email": row[2],
            "email": decrypt(row[3]) or "N/A",
            "password": "****** (SHA-256 Hashed - Irreversible)",
            "dob": decrypt(row[5]) or "N/A",
            "position": decrypt(row[6]) or "N/A",
            "salary": decrypt(row[7]) or "N/A",
            "phone": decrypt(row[8]) or "N/A",
            "address": decrypt(row[9]) or "N/A",
            "department": decrypt(row[10]) or "N/A",
            "hire_date": decrypt(row[11]) or "N/A",
            "emergency_contact": decrypt(row[12]) or "N/A",
            "profile_picture": decrypt(row[13]) if row[13] else None,
            "country": decrypt(row[14]) or "N/A",
            "bio": decrypt(row[15]) or "N/A",
            "linkedin": decrypt(row[16]) or "N/A",
            "twitter": decrypt(row[17]) or "N/A"
        })
    
    return render_template('admin_decrypted.html', 
                           columns=list(decrypted_rows[0].keys()) if decrypted_rows else columns,
                           rows=decrypted_rows,
                           title="Decrypted Employee Data (Admin Only)")

@app.route('/ddos_dashboard')
def ddos_dashboard():
    metrics_file = "ddos_metrics.json"
    if not os.path.exists(metrics_file):
        return "<h1 style='color:red;text-align:center'>No metrics yet.<br>Run ddos_simulator.py first.</h1>"

    metrics = []
    with open(metrics_file, 'r') as f:
        for line in f:
            if line.strip():
                metrics.append(json.loads(line))

    if not metrics:
        return "<h1 style='color:red;text-align:center'>Metrics file is empty. Start ddos_simulator.py</h1>"

    timestamps = [m['timestamp'] for m in metrics]
    requests_sent = [m['requests_per_second'] for m in metrics]
    aes_times = [m['aes_encryption_time_ms'] for m in metrics]
    sha_times = [m['sha256_hash_time_ms'] for m in metrics]

    latest_requests = requests_sent[-1] if requests_sent else 0
    latest_aes = aes_times[-1] if aes_times else 0
    attack_intensity = min(100, int((latest_requests / 3.2) + (latest_aes * 4.2) + random.randint(0, 12)))

    if attack_intensity >= 70:
        send_intruder_alert(attack_intensity)

    attack_banner = ""
    if attack_intensity > 80:
        attack_banner = '''
        <div style="background:#8B0000; color:white; padding:18px; font-size:1.5em; font-weight:bold; 
                    animation: flash 1.2s infinite; margin:20px 0; border-radius:8px;">
            🚨 ATTACK IN PROGRESS - HIGH INTENSITY DDoS DETECTED
        </div>
        <style>@keyframes flash { 50% {opacity: 0.3;} }</style>
        '''

    fig_intensity = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=attack_intensity,
        title={'text': "🔥 ATTACK INTENSITY", 'font': {'size': 36, 'color': '#ff2222'}},
        delta={'reference': 60, 'increasing': {'color': "#ff0000"}},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "#ff0000"},
            'bgcolor': "#1a1a1a",
            'borderwidth': 5,
            'steps': [
                {'range': [0, 40], 'color': '#00cc00'},
                {'range': [40, 70], 'color': '#ffcc00'},
                {'range': [70, 100], 'color': '#ff0000'}
            ]
        }
    ))
    fig_intensity.update_layout(template='plotly_dark', height=360, margin=dict(t=100, b=40))
    intensity_html = pio.to_html(fig_intensity, full_html=False, include_plotlyjs='cdn')

    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=timestamps, y=requests_sent, mode='lines+markers', name='Requests/sec',
                             line=dict(color='#ff3366', width=5), marker=dict(size=7, color='#ff6699')))
    fig1.update_layout(title='DDoS Traffic Spike Simulation', xaxis_title='Time', yaxis_title='Requests per Second',
                       template='plotly_dark', height=580, plot_bgcolor='#0a0a0a')

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=timestamps, y=aes_times, mode='lines+markers', name='AES (ms)', line=dict(color='#00ccff', width=3.5)))
    fig2.add_trace(go.Scatter(x=timestamps, y=sha_times, mode='lines+markers', name='SHA-256 (ms)', line=dict(color='#ffaa00', width=3.5)))
    fig2.update_layout(title='Encryption & Hashing Overhead During Simulated Attack',
                       xaxis_title='Time', yaxis_title='Time (milliseconds)', template='plotly_dark', height=520)

    graph1 = pio.to_html(fig1, full_html=False, include_plotlyjs='cdn')
    graph2 = pio.to_html(fig2, full_html=False, include_plotlyjs='cdn')

    detection_options = ["HIGH-RATE FLOOD DETECTED", "MULTIPLE FAILURES DETECTED", "ENCRYPTION TIMING ANOMALY",
                         "RESOURCE EXHAUSTION ALERT", "SYN FLOOD DETECTED", "CRITICAL ATTACK INTENSITY"]
    
    table_rows = ""
    for m in metrics[-12:]:
        detection = m.get('detection_result', random.choice(detection_options))
        color = "#ff2222" if attack_intensity >= 75 else "#ffaa00"
        table_rows += f"""
        <tr>
            <td>{m['timestamp']}</td>
            <td><strong>{m['requests_per_second']}</strong></td>
            <td>{m['aes_encryption_time_ms']:.1f}</td>
            <td>{m['sha256_hash_time_ms']:.1f}</td>
            <td style="color:{color}; font-weight:bold;">{detection}</td>
        </tr>
        """

    html = f"""
    <html>
    <head><title>REAL-TIME DDoS ATTACK SIMULATION DASHBOARD</title>
    <meta http-equiv="refresh" content="8">
    <style>
        body {{ background:#0a0a0a; color:#0f0; font-family:Arial,sans-serif; text-align:center; margin:0; padding:20px; }}
        h1 {{ color:#ff4444; }}
        table {{ margin:30px auto; border-collapse:collapse; width:92%; background:#111; }}
        th, td {{ padding:15px; border:1px solid #444; }}
        th {{ background:#1f1f1f; color:white; }}
    </style>
    </head>
    <body>
        <h1>🚨 REAL-TIME DDoS ATTACK SIMULATION DASHBOARD</h1>
        <p class="subtitle">Live TLS Encrypted Traffic on port 5000</p>
        {attack_banner}
        {intensity_html}
        {graph1}
        {graph2}
        <h2 style="color:#ffaa00;">Live Detection Results</h2>
        <table>
            <tr><th>Time</th><th>Requests/sec</th><th>AES (ms)</th><th>SHA-256 (ms)</th><th>Detection Status</th></tr>
            {table_rows}
        </table>
    </body>
    </html>
    """
    return html


# ====================== START SERVER ======================
if __name__ == '__main__':
    run_with_tls()