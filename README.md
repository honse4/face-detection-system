This project aims to mix in elements of machine learning and web development while providing real-life solutions.

With this app, an employer can keep track of each employees' attendance without having to manually mark it. The empolyer can enter all their employees in the database
using their image and name, then use campera input to recognize and automatically mark any employee. The system will keep track of attendances for each employee annd store it 
so that it can be viewed at any time.

The project uses flask for the backend, sqlalchemy for the database, face_recognition and cv2 for the actual processing and recognition of people. To avoid a major load on the backend, 
the frames caught by the camera are sent in batches, and only the frames which have faces on them are used. This is done by having a small but effective js face recognition model, that can 
recognise faces in an image. These images are then sent to the face_recognition python library, which is trained on the employees database, and it decides to mark an emplyee if they are recognised, 
which it provides confirmation of.
