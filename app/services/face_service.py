import numpy as np
import tensorflow
from deepface import DeepFace
from sklearn.metrics.pairwise import cosine_similarity
from app.models import Student

def process_images(image_paths):
    """Generate average embedding for multiple images."""
    embeddings = []
    for path in image_paths:
        print(f"Processing image: {path}")
        embedding = DeepFace.represent(path, model_name="Facenet")[0]["embedding"]
        embeddings.append(embedding)

    return np.mean(embeddings, axis=0).tolist()

def recognize_face(image_path):
    """Recognize a face from an image."""
    print(f"Recognizing face from image: {image_path}")
    try:
        new_embedding = DeepFace.represent(image_path, model_name="Facenet", enforce_detection=False)[0]["embedding"]
    except ValueError as e:
        print(f"Error: {e}")
        return None, 0.0

    max_similarity = 0
    recognized_student = None

    # Compare against database
    for student in Student.get_all_students():
        print(f"Comparing against student: {student['student_id']}")
        db_embedding = np.array(student["embedding"])
        similarity = cosine_similarity([new_embedding], [db_embedding])[0][0]
        if similarity > max_similarity:
            max_similarity = similarity
            recognized_student = student["student_id"]
    
    print(f"Recognized student: {recognized_student}, Similarity: {max_similarity}")
    return recognized_student, max_similarity