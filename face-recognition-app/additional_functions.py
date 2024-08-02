import numpy as np
import face_recognition
import json
import cv2
import base64
from db import get_db, get_all_employees, employee_present, get_employee_attendances, add_date, get_all_dates
from datetime import datetime

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
temp_storage = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def encode_face_encoding(face_encoding):
    return json.dumps(face_encoding.tolist())

def decode_face_encoding(face_encoding_str):
    return np.array(json.loads(face_encoding_str))

def image_to_encoding(filename):
    image = face_recognition.load_image_file(f'uploads/{filename}')
    face_encodings = face_recognition.face_encodings(image)
    face_encoding_str = ''
    if face_encodings:
        face_encoding = face_encodings[0]
        face_encoding_str = encode_face_encoding(face_encoding)
    
    return face_encoding_str


def fill_names(ctr_id):
    with get_db() as db_:
        emps = get_all_employees(db_, ctr_id)
           
    info = {'encodings': [], 'names' :[], 'ids': []}     

    for emp in emps:
        info['encodings'].append(decode_face_encoding(emp.image_encoding)) 
        info['ids'].append(emp.id)
        info['names'].append(f'{emp.firstname} {emp.lastname}')
    
    temp_storage[ctr_id] = info

def attendance_time(employee_attendances, time):
    with get_db() as db_:
        all_dates = get_all_dates(db_)
    
    if time == "Month":
        dates = [date for (date,) in all_dates if is_date_in_current_month(date)]  
        print(dates) 
    elif time == "Week":
        dates = [date for (date,) in all_dates if is_date_in_current_week(date)]
    elif time == "Year":
        dates = [date for (date,) in all_dates if is_date_in_current_year(date)]
    else:
        dates = [date for (date,) in all_dates]
    
    counter = 0
    for (employee_date, ) in employee_attendances:
        if employee_date in dates:
            counter+=1
    
    return dict_with_values(counter, dates)
        
    
def is_date_in_current_month(date_to_check):
    now = datetime.now()
    
    current_month = now.month
    current_year = now.year
    
    return date_to_check.month == current_month and date_to_check.year == current_year    

def is_date_in_current_week(date_to_check):
    now = datetime.now()
    current_year, current_week, _ = now.isocalendar()
    check_year, check_week, _ = date_to_check.isocalendar()
    
    return check_year == current_year and check_week == current_week 

def is_date_in_current_year(date_to_check):
    now = datetime.now()
    current_year = now.year
    
    return date_to_check.year == current_year


def dict_with_values(counter, dates):
    info = {}
    info['counter'] = counter
    if len(dates)>0:
        info['percent'] = (counter/len(dates))*100
    else:
        info['percent'] = 0
    return info
    

def record_faces(frames, ctr_id): 
    info = temp_storage[ctr_id]
    known_face_encodings = info['encodings']
    known_ids = info['ids']
    known_names = info['names']
    
    with get_db() as db_:
        add_date(db_)
    
    for frame_data in frames:
        img_data = base64.b64decode(frame_data.split(',')[1])
        np_img = np.frombuffer(img_data, dtype=np.uint8)

        frame = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
        rgb_frame = np.ascontiguousarray(frame[:, :, ::-1])
    
        face_locations = face_recognition.face_locations(rgb_frame)
        if not face_locations:
            continue
            
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.5)
        
            if True in matches:
                first_match_index = matches.index(True)
                known_face_encodings.pop(first_match_index)
                name = known_names.pop(first_match_index)
                id = known_ids.pop(first_match_index)
                with get_db() as db_:
                    if datetime.now().date() in [att.timestamp for att in get_employee_attendances(db_, id)]:
                        continue
                    employee_present(db_, id)    
                return name
                