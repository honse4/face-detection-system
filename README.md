<h1>Employee Attendance Tracking App</h1>

This project aims to integrate machine learning and web development to provide a real-life solution for tracking employee attendance. The app allows employers to keep track of each employee's attendance without manual intervention. Employers can enter their employees into the database using their image and name, and the system will automatically recognize and mark attendance using camera input. The system stores attendance records for each employee, which can be viewed at any time.

The app offers real-time facial recognition using a ResNet model, ensuring accurate and efficient identification of employees. Employee data is stored securely, and attendance statistics are readily available for review. The backend is built using Flask, while SQLAlchemy manages the database. OpenCV (cv2) is utilized for image processing and recognition, and a JavaScript face detection model pre-filters frames to optimize performance.

The app captures frames in real time using a camera. A lightweight JavaScript face detection model pre-filters these frames, sending only those with detected faces to the backend. OpenCV (cv2) preprocesses the images and extracts features, which are then classified by the ResNet model to identify employees. Employee data is stored in a database managed by SQLAlchemy,
