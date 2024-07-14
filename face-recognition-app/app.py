from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = 'test123'

users = {
    "testuser": "password123"
}

@app.route('/')
def home():
    return render_template('login.html')


@app.route('/validate', methods=['POST'])
def validate():
    username = request.form['username']
    password = request.form['password']
    
    if username in users and users[username] == password:
        session['username'] = username
        flash('Login successful!', 'success')
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('home'))
    
@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html')
    else:
        return redirect(url_for('home'))

@app.route('/attendance')
def attendance():
    return render_template('attendance.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))
    
if __name__ == '__main__':
    app.run(debug=True)
