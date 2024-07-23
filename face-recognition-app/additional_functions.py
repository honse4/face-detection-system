import numpy as np
import face_recognition
import json
import cv2
import base64
from db import get_db, get_all_employees

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
known_face_encodings = [] 
known_face_names = [] 

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
         
    for emp in emps:
        known_face_encodings.append(decode_face_encoding(emp.image_encoding))
        known_face_names.append(emp.firstname)


def record_faces(frames):   
        
    video_capture = cv2.VideoCapture(0)
    if not video_capture.isOpened():
        print("Error: Could not open camera.")

    for frame_data in frames:
        img_data = base64.b64decode(frame_data.split(',')[1])
        np_img = np.frombuffer(img_data, dtype=np.uint8)

        frame = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
        rgb_frame = frame[:, :, ::-1]
    
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
    
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        
            name = "Unknown"
            if True in matches:
                first_match_index = matches.index(True)
                name = known_face_names[first_match_index]
                print(name)
        
        cv2.imshow('Video', frame)
    
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()
    