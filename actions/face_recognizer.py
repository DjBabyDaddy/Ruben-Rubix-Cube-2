import os
import time
from tts import edge_speak

try:
    import cv2
    import numpy as np
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    cv2 = None
    np = None
    print("ℹ️ OpenCV not installed. Facial recognition disabled. Install opencv-contrib-python to enable.")

FACES_DIR = "memory/known_faces"
face_recognizer = None
face_cascade = None
label_map = {}

def initialize_facial_matrix():
    global face_recognizer, face_cascade, label_map
    if not OPENCV_AVAILABLE:
        print("ℹ️ Facial recognition skipped — OpenCV not available.")
        return
    print("🧠 RUBE Loading Optimized Facial Recognition Matrix...")
    
    if not os.path.exists(FACES_DIR):
        os.makedirs(FACES_DIR)
        print(f"⚠️ Created {FACES_DIR}. Please add folders with names and photos to enable facial recognition.")
        return

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    face_recognizer = cv2.face.LBPHFaceRecognizer_create()
    
    faces = []
    labels = []
    current_label = 0
    
    for person_name in os.listdir(FACES_DIR):
        person_dir = os.path.join(FACES_DIR, person_name)
        if not os.path.isdir(person_dir): continue
            
        label_map[current_label] = person_name
        for image_name in os.listdir(person_dir):
            img_path = os.path.join(person_dir, image_name)
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            if img is None: continue
                
            detected_faces = face_cascade.detectMultiScale(img, scaleFactor=1.2, minNeighbors=5)
            for (x, y, w, h) in detected_faces:
                faces.append(img[y:y+h, x:x+w])
                labels.append(current_label)
        current_label += 1

    if faces:
        face_recognizer.train(faces, np.array(labels))
        print(f"✅ Facial Matrix Online. Recognized {len(label_map)} known identities.")
    else:
        face_recognizer = None
        print("⚠️ Facial Matrix Empty. No valid faces found in memory/known_faces.")

def identity_scan_room(parameters, response, player, session_memory):
    global face_recognizer, face_cascade, label_map
    if not OPENCV_AVAILABLE:
        edge_speak("Boss, facial recognition requires OpenCV. It's not installed on this system.", player)
        return
    time.sleep(1.2)

    if face_recognizer is None or face_cascade is None:
        edge_speak("Boss, the facial recognition matrix is empty. Please add photos to my memory folder.", player)
        return

    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        edge_speak("Boss, I cannot activate the camera feed to scan the room.", player)
        return
        
    ret, frame = cam.read()
    cam.release()
    
    if not ret: return
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5)
    
    if len(faces) == 0:
        edge_speak("I do not detect any human faces in my field of view, boss.", player)
        return
        
    recognized_names = []
    for (x, y, w, h) in faces:
        face_roi = gray[y:y+h, x:x+w]
        label, confidence = face_recognizer.predict(face_roi)
        if confidence < 80: 
            recognized_names.append(label_map.get(label, "Unknown"))

    recognized_names = list(set(recognized_names))
    
    if recognized_names:
        names_str = " and ".join(recognized_names)
        edge_speak(f"Scanning complete, boss. I see {names_str} in the room.", player)
    else:
        edge_speak("I detect a face, boss, but it does not match any identities in my local database.", player)