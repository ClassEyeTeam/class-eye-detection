import numpy as np
import tensorflow
from deepface import DeepFace
from sklearn.metrics.pairwise import cosine_similarity
from app.models import Student
import cv2
import time
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def has_face_quick_check(image_path):
    """
    Quick face detection using a simple Haar cascade.
    Returns True if at least one face is found, otherwise False.
    """
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return False
    faces = cascade.detectMultiScale(img, scaleFactor=1.3, minNeighbors=5, minSize=(30, 30))
    return len(faces) > 0


def process_images(image_paths):
    """Generate average embedding for multiple images."""
    start_time = time.time()
    embeddings = []
    for path in image_paths:
        logger.info(f"Processing image: {path}")
        image_start_time = time.time()
        embedding = DeepFace.represent(path, model_name="Facenet")[0]["embedding"]
        image_end_time = time.time()
        logger.info(f"Time taken to process image {path}: {image_end_time - image_start_time:.2f} seconds")
        embeddings.append(embedding)

    average_embedding = np.mean(embeddings, axis=0).tolist()
    end_time = time.time()
    logger.info(f"Total time taken to process all images: {end_time - start_time:.2f} seconds")
    return average_embedding

def recognize_face(image_path):
    """
    Check for faces quickly with Haar cascade; if found, run DeepFace embedding and compare.
    """
    start_time = time.time()
    logger.info(f"Recognizing face from image: {image_path}")

    # Quick skip: If no face is found, return immediately
    if not has_face_quick_check(image_path):
        logger.info("Quick check: No face detected.")
        return None, 0.0

    # Detailed recognition with DeepFace
    try:
        embedding_data = DeepFace.represent(
            image_path, model_name="Facenet", enforce_detection=False
        )
        new_embedding = embedding_data[0]["embedding"]
    except Exception as e:
        logger.error(f"Error generating DeepFace embedding: {e}")
        return None, 0.0

    max_similarity = 0
    recognized_student = None

    # Compare against database
    for student in Student.get_all_students():
        logger.info(f"Comparing against student: {student['student_id']}")
        db_embedding = np.array(student["embedding"])
        similarity = cosine_similarity([new_embedding], [db_embedding])[0][0]
        if similarity > max_similarity:
            max_similarity = similarity
            recognized_student = student["student_id"]

    end_time = time.time()
    logger.info(f"Recognized student: {recognized_student}, Similarity: {max_similarity}")
    logger.info(f"Total time taken to recognize face: {end_time - start_time:.2f} seconds")
    return recognized_student, max_similarity