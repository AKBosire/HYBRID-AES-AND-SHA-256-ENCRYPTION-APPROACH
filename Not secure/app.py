from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Simple in-memory "database"
registered_users = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_data = {
            'name': request.form['name'],
            'email': request.form['email'],
            'password': request.form['password'],
            'phone': request.form['phone'],
            'dob': request.form['dob'],
            'position': request.form['position'],
            'salary': request.form['salary'],
            'department': request.form['department'],
            'address': request.form['address'],
            'emergency_contact': request.form['emergency_contact']
        }
        registered_users.append(user_data)
        return f"<h3>Registered Successfully</h3><pre>{user_data}</pre>"
    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True)
