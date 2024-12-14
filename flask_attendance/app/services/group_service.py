import cv2
from mtcnn import MTCNN
from .face_service import recognize_face
import os
import numpy as np

detector = MTCNN()

def process_group_photo(image_path, upload_folder):
    """Process group photo and return recognized students."""
    img = cv2.imread(image_path)
    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Detect faces
    faces = detector.detect_faces(rgb_img)
    recognized_students = []

    # Process each detected face
    for i, face in enumerate(faces):
        x, y, width, height = face['box']
        face_img = rgb_img[y:y+height, x:x+width]
        
        # Save individual face temporarily
        face_path = os.path.join(upload_folder, f'face_{i}.jpg')
        cv2.imwrite(face_path, cv2.cvtColor(face_img, cv2.COLOR_RGB2BGR))
        
        try:
            # Recognize the face
            student_id, confidence = recognize_face(face_path)
            
            if student_id and confidence > 0.6:
                recognized_students.append({
                    "student_id": student_id,
                    "confidence": confidence
                })
        finally:
            if os.path.exists(face_path):
                os.remove(face_path)

    return recognized_students, len(faces)