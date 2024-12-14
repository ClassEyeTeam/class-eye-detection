
import cv2
import numpy as np
from mtcnn import MTCNN
from deepface import DeepFace
import os

detector = MTCNN()

def detect_and_crop(image_path):
    image = cv2.imread(image_path)
    results = detector.detect_faces(image)

    if results:
        x, y, w, h = results[0]['box']
        cropped_face = image[y:y+h, x=x+w]
        return cropped_face
    else:
        raise ValueError("No face detected!")

def extract_embedding(face_image):
    temp_file = "temp_face.jpg"
    cv2.imwrite(temp_file, face_image)
    embedding = DeepFace.represent(temp_file, model_name="Facenet")[0]["embedding"]
    os.remove(temp_file)
    return np.array(embedding)