from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory, jsonify, flash, get_flashed_messages
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
import os
from db import get_db, add_user, add_employee, get_user, init_db, get_all_employees, get_employee, get_employee_one_name, delete_employee, get_user_by_id, get_employee_by_id, edit_employee_image,edit_employee_no_image, get_employee_attendances
from additional_functions import allowed_file, image_to_encoding, record_faces, fill_names
import zlib
import json

app = Flask(__name__)
app.secret_key = 'test123'
login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = 'login'

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


@login_manager.user_loader
def load_user(user_id):
    with get_db() as db_:
        return get_user_by_id(db_, user_id)

@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/validate', methods=['POST'])
def validate():
    username = request.form['username']
    password = request.form['password']
    
    with get_db() as db_:
        user = get_user(db_, username)
    
        if user is not None:
            if user.username == username and user.password == password:
                session['username'] = username
                session['id'] = user.id
                login_user(user)
                return redirect(url_for('home'))        
        else:
            flash('Invalid username or password', 'error')
            return redirect(url_for('login'))
    
@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/registration',methods=['POST'])
def registrate():
    username = request.form['username']
    password = request.form['password']
    
    with get_db() as db_:
        user = get_user(db_, username)
    
        if user is None:      
            session['username'] = username
            add_user(db_, username, password)
        
            user_ = get_user(db_, username)
            session['id'] = user_.id
            login_user(user_)        
            return redirect(url_for('home'))        
        else:
            flash('Username already taken', 'error')
            return redirect(url_for('register'))
        
@app.route('/')
@login_required
def dash():
    return redirect(url_for('home')) 
    
@app.route('/dashboard')
@login_required
def home():
    return render_template('dashboard.html')

@app.route('/employee-attendance-all')
@login_required
def send_employee_attendance_all():
    with get_db() as db_:
        emps = get_all_employees(db_, current_user.id)
            
        atts = []
        for emp in emps:
            dict = {}
            dict['name'] = emp.firstname + ' ' + emp.lastname
            dict['length'] = len(get_employee_attendances(db_, emp.id))   
            atts.append(dict)   
    return jsonify(atts)

@app.route('/employee-attendance-search/<string:search>')
@login_required
def send_employee_attendance_search(search):
    name_list = search.split()
    with get_db() as db_:
        if len(name_list) == 1:
                emps = get_employee_one_name(db_, name_list[0], session['id'])
        else: 
                emps = get_employee(db_, name_list[0], name_list[1], session['id'])
        atts = []
        for emp in emps:
            dict = {}
            dict['name'] = emp.firstname + ' ' + emp.lastname
            dict['length'] = len(get_employee_attendances(db_, emp.id))   
            atts.append(dict) 
    
    return jsonify(atts)

@app.route('/attendance')
@login_required
def attendance():
    if request.args.get('search'):
        search_result = request.args.get('search')
        name_list = search_result.split()
        
        with get_db() as db_:
            if len(name_list) == 1:
                emps = get_employee_one_name(db_, name_list[0], current_user.id)
            else: 
                emps = get_employee(db_, name_list[0], name_list[1], current_user.id)
    else:
        with get_db() as db_:
            emps = get_all_employees(db_, current_user.id)
            
    atts = {}
    for emp in emps:
        atts[f'{emp.firstname} {emp.lastname}'] = len(get_employee_attendances(db_, emp.id))      
    return render_template('attendance.html', atts = atts)    
    
@app.route('/logout')
@login_required
def logout():
    session.pop('username', None)
    session.pop('id', None)
    logout_user()
    return redirect(url_for('login'))
    


@app.route('/add-new')
@login_required
def add() :
    return render_template('add.html')
    
@app.route('/add-new/add', methods=['POST'])
@login_required
def upload_file():
    if 'image' not in request.files:
        flash('No image uploaded', 'error')
        return redirect(url_for('add'))
    
    file = request.files['image']
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('add'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        face_encoding_str = image_to_encoding(filename)
        if not face_encoding_str:
            flash('Invalid image', 'error')
            return redirect(url_for('add'))
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        
        id = current_user.id
        with get_db() as db_:
            add_employee(db_, firstname, lastname, filename, face_encoding_str, id)
        
        flash('New Employee Added', 'success')
        return redirect(url_for('add'))
    
    flash('Invalid file type. Use jpeg, jpg or png', 'error')
    return redirect(url_for('add'))


@app.route('/employee-data-all')
@login_required
def send_employee_data_all():
    with get_db() as db_:
            emps = get_all_employees(db_, current_user.id)
    
    return jsonify([emp.to_dict() for emp in emps])

@app.route('/employee-data-search/<string:search>')
@login_required
def send_employee_data_search(search):
    name_list = search.split()
    with get_db() as db_:
        if len(name_list) == 1:
                emps = get_employee_one_name(db_, name_list[0], session['id'])
        else: 
                emps = get_employee(db_, name_list[0], name_list[1], session['id'])
    
    return jsonify([emp.to_dict() for emp in emps])


@app.route('/edit')
@login_required
def edit() :
    if request.args.get('search'):
        search_result = request.args.get('search')
        name_list = search_result.split()
        
        with get_db() as db_:
            if len(name_list) == 1:
                emps = get_employee_one_name(db_, name_list[0], session['id'])
            else: 
                emps = get_employee(db_, name_list[0], name_list[1], session['id'])
    else:
        with get_db() as db_:
            emps = get_all_employees(db_, session['id'])
            
    emps_json = [emp.to_dict() for emp in emps]        
    return render_template('edit.html', emps=emps_json)

@app.route('/edit/delete', methods=['POST'])
@login_required
def delete():
    emp_id = request.json
    with get_db() as db_:
        emp = delete_employee(db_, emp_id)
        if emp:
            return redirect(url_for('edit'))
        else:
            return {"status": "error"}
    
@app.route('/edit/<int:employee_id>')
@login_required
def edit_one(employee_id):
    with get_db() as db_:
        emp = get_employee_by_id(db_, employee_id)
    
        if emp and emp.controller_id == current_user.id:
            return render_template('edit-one.html', emp=emp)
        else:
            return redirect(url_for('edit'))
   
@app.route('/edit/info', methods=['POST'])
@login_required
def edit_one_handler():
    firstname = request.form.get('firstname')
    lastname = request.form.get('lastname')
    id = request.form.get('id')
    file = request.files['image']
    
    with get_db() as db_: 
        if file:
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                face_encoding_str = image_to_encoding(filename)
                
                if not face_encoding_str:
                    flash('Invalid image', 'error')
                    return redirect(url_for('edit_one', employee_id=id))
                edit_employee_image(db_,id, firstname, lastname, filename)   
            else:
                flash('Invalid file type. Use jpeg, jpg or png', 'error')    
                return redirect(url_for('edit_one', employee_id=id))    
        else:
            edit_employee_no_image(db_, id, firstname, lastname)
    flash('Edit Saved', 'success') 
    return redirect(url_for('edit'))
       
    
@app.route('/record-attendance')
@login_required
def record():
    fill_names(current_user.id)
    return render_template('record.html')


@app.route('/upload-frames', methods=['POST'])
@login_required
def upload_frames():
    compressed_data = request.data
    decompressed_data = zlib.decompress(compressed_data)
    frames = json.loads(decompressed_data)
        
    results = record_faces(frames, current_user.id)
    return jsonify(results)
        
    
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
