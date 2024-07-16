from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from werkzeug.utils import secure_filename
import os
import uuid
from db import get_db, add_user, add_employee, get_user, init_db, get_all_employees, get_employee, get_employee_one_name

app = Flask(__name__)
app.secret_key = 'test123'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/validate', methods=['POST'])
def validate():
    username = request.form['username']
    password = request.form['password']
    
    db_ = next(get_db())
    user = get_user(db_, username)
    
    if user is not None:
        if user.username == username and user.password == password:
            session['username'] = username
            session['id'] = user.id
            return redirect(url_for('home'))        
    else:
        return redirect(url_for('login'))
    
@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/registration',methods=['POST'])
def registrate():
    username = request.form['username']
    password = request.form['password']
    
    db_ = next(get_db())
    user = get_user(db_, username)
    
    if user is None:      
        session['username'] = username
        add_user(db_, username, password)
        
        user_ = get_user(db_, username)
        session['id'] = user_.id
                
        return redirect(url_for('home'))        
    else:
        return redirect(url_for('register'))
    
@app.route('/')
def home():
    if 'username' in session:
        return render_template('dashboard.html')
    else:
        return redirect(url_for('login'))

@app.route('/attendance')
def attendance():
    if 'username' in session:
        return render_template('attendance.html')
    else:
        return redirect(url_for('login'))
    
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))



@app.route('/add-new')
def add() :
    if 'username' in session:
        return render_template('add.html')
    else:
        return redirect(url_for('login'))
    
@app.route('/add-new/add', methods=['POST'])
def upload_file():
    if 'image' not in request.files:
        print("No image")
        return redirect(url_for('add'))
    
    file = request.files['image']
    if file.filename == '':
        print('No selected file')
        return redirect(url_for('add'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        id = session['id']
        db = next(get_db())
        add_employee(db, firstname, lastname, filename, id)
        
        print('File successfully uploaded')
        return redirect(url_for('add'))
    print('invlid file type')
    return redirect(url_for('add'))



@app.route('/edit')
def edit() :
    if 'username' in session:
        if request.args.get('search'):
            search_result = request.args.get('search')
            name_list = search_result.split()
            db_ = next(get_db())
    
            if len(name_list) == 1:
                emps = get_employee_one_name(db_, name_list[0], session['id'])
            else: 
                emps = get_employee(db_, name_list[0], name_list[1], session['id'])
        else:
            db_ = next(get_db())
            emps = get_all_employees(db_, session['id'])
         
        return render_template('edit.html', emps=emps)
    else:
        return redirect(url_for('login'))
    
    
    
@app.route('/record-attendance')
def record():
    if 'username' in session:
        return render_template('record.html')
    else:
        return redirect(url_for('login'))

    
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
