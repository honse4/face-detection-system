import numpy as np
import face_recognition
import json
import cv2
import base64
from db import get_db, get_all_employees, employee_present, get_employee_attendances
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
    

def record_faces(frames, ctr_id): 
    info = temp_storage[ctr_id]
    known_face_encodings = info['encodings']
    known_ids = info['ids']
    known_names = info['names']
    
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
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        
            if True in matches:
                first_match_index = matches.index(True)
                known_face_encodings.pop(first_match_index)
                name = known_names.pop(first_match_index)
                id = known_ids.pop(first_match_index)
                with get_db() as db_:
                    if datetime.now().date() in [att.timestamp.date() for att in get_employee_attendances(db_, id)]:
                        continue
                    employee_present(db_, id)    
                return name
                