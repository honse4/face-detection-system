from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory, jsonify, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
import os
from db import get_db, add_user, add_employee, get_user, init_db, get_all_employees, get_employee, get_employee_one_name, delete_employee, get_user_by_id, get_employee_by_id, edit_employee_image,edit_employee_no_image, get_employee_attendances, get_all_dates
from additional_functions import allowed_file, image_to_encoding, record_faces, fill_names, attendance_time
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

def delete_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.isfile(file_path):
        os.remove(file_path)
        return jsonify({"message": "File deleted successfully"}), 200
    else:
        return jsonify({"error": "File not found"}), 404

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

@app.route('/employee-attendance')
@login_required
def send_employee_attendance():
    search = request.args.get('search', default=None)
    time = request.args.get('time', default='Month')
    
    with get_db() as db_:
        if search != "All":
            name_list = search.split()
            if len(name_list) == 1:
                emps = get_employee_one_name(db_, name_list[0], session['id'])
            else: 
                emps = get_employee(db_, name_list[0], name_list[1], session['id'])
        else:
            emps = get_all_employees(db_, current_user.id)
             
        atts = []
        for emp in emps:
            emp_attendances = get_employee_attendances(db_, emp.id)
            dict = {}
            dict['id'] = emp.id
            dict['name'] = emp.firstname + ' ' + emp.lastname
            dict.update(attendance_time(emp_attendances, time))
            atts.append(dict)   
    return jsonify(atts)


@app.route('/attendance/one-employee/<int:id>')
@login_required
def get_attendance_one(id):
    times = ["Week", "Month", "Year", "All"]
    dict = {}
    with get_db() as db_:
        atts = get_employee_attendances(db_, id)
        dict['atts'] = [date.strftime('%Y-%m-%d') for (date,) in atts[-10:]]
        dict['dates'] = [date.strftime('%Y-%m-%d') for (date,) in get_all_dates(db_)[-10:]]
        for time in times:
            dict[time] = attendance_time(atts, time)
        
        
    return jsonify(dict)


@app.route('/attendance')
@login_required
def attendance():     
    return render_template('attendance.html')    

@app.route('/attendance/<int:employee_id>')
@login_required
def attendance_one(employee_id):
    with get_db() as db_:
        emp = get_employee_by_id(db_, employee_id)
        if emp and emp.controller_id == current_user.id:
            return render_template('attendance-one.html', emp=emp)
        else:
            return redirect(url_for('attendance'))


        
    
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
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if not os.path.isfile(file_path):
            file.save(file_path)
            face_encoding_str = image_to_encoding(filename)
            if not face_encoding_str:
                delete_file(filename)
                flash('Invalid image', 'error')
                return redirect(url_for('add'))
              
            firstname = request.form['firstname']
            lastname = request.form['lastname']
        
            id = current_user.id
            with get_db() as db_:
                add_employee(db_, firstname, lastname, filename, face_encoding_str, id)
        
            flash('New Employee Added', 'success')
            return redirect(url_for('add'))
        else:
            flash('Invalid image', 'error')
            return redirect(url_for('add'))
    
    flash('Invalid file type. Use jpeg, jpg or png', 'error')
    return redirect(url_for('add'))


@app.route('/employee-info/<string:search>')
@login_required
def employee_info(search):
    with get_db() as db_:
        if search != "All":
            name_list = search.split()
            if len(name_list) == 1:
                emps = get_employee_one_name(db_, name_list[0], session['id'])
            else: 
                emps = get_employee(db_, name_list[0], name_list[1], session['id'])
        else:
            emps = get_all_employees(db_, current_user.id)
    
    return jsonify([emp.to_dict() for emp in emps])


@app.route('/edit')
@login_required
def edit() :       
    return render_template('edit.html')

@app.route('/edit/delete', methods=['POST'])
@login_required
def delete():
    emp_id = request.json
    with get_db() as db_:
        emp = delete_employee(db_, emp_id)
        if emp:
            delete_file(emp.image_path)
            return {"status": "Success"}
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
                
                if not os.path.isfile(file_path):
                    file.save(file_path)
                    face_encoding_str = image_to_encoding(filename)                
                    if not face_encoding_str:
                        delete_file(filename)
                        flash('Invalid image', 'error')
                        return redirect(url_for('edit_one', employee_id=id))
                
                    emp = get_employee_by_id(db_, id)
                    delete_file(emp.image_path)
                
                    edit_employee_image(db_,id, firstname, lastname, filename, face_encoding_str)   
                else:
                    flash('Invalid image', 'error')
                    return redirect(url_for('edit_one', employee_id=id))
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
