from flask import Flask, request, jsonify
from pymongo import MongoClient
import os
import cv2
import numpy as np
from mtcnn import MTCNN
from deepface import DeepFace
from sklearn.metrics.pairwise import cosine_similarity
import requests

# Initialize Flask app
app = Flask(__name__)

# MongoDB connection
mongo_client = MongoClient("mongodb://localhost:27017")
db = mongo_client["attendance_db"]
students_collection = db["students"]

# Face detection and embedding tools
detector = MTCNN()

# Threshold for face similarity
SIMILARITY_THRESHOLD = 0.8

# --- Utility Functions ---
def detect_and_crop(image_path):
    """Detect and crop the face from the image."""
    image = cv2.imread(image_path)
    results = detector.detect_faces(image)

    if results:
        x, y, w, h = results[0]['box']
        cropped_face = image[y:y+h, x:x+w]
        return cropped_face
    else:
        raise ValueError("No face detected!")

def extract_embedding(face_image):
    """Generate an embedding for a face image."""
    temp_file = "temp_face.jpg"
    cv2.imwrite(temp_file, face_image)
    embedding = DeepFace.represent(temp_file, model_name="Facenet")[0]["embedding"]
    os.remove(temp_file)  # Clean up
    return np.array(embedding)

# --- Routes ---
@app.route("/students/add", methods=["POST"])
def add_student():
    """Add a student with ID and images."""
    data = request.json
    student_id = data.get("student_id")
    image_paths = data.get("images")  # List of image paths

    if not student_id or not image_paths:
        return jsonify({"error": "Student ID and images are required"}), 400

    # Process images and compute average embedding
    embeddings = []
    for path in image_paths:
        cropped_face = detect_and_crop(path)
        embedding = extract_embedding(cropped_face)
        embeddings.append(embedding)

    avg_embedding = np.mean(embeddings, axis=0).tolist()  # Convert to list for MongoDB

    # Save to database
    students_collection.insert_one({
        "student_id": student_id,
        "embedding": avg_embedding
    })

    return jsonify({"message": f"Student {student_id} added successfully"}), 201

@app.route("/students/recognize", methods=["POST"])
def recognize_student():
    """Recognize a student from an image."""
    data = request.json
    image_path = data.get("image_path")
    if not image_path:
        return jsonify({"error": "Image path is required"}), 400

    # Detect and embed face
    cropped_face = detect_and_crop(image_path)
    new_embedding = extract_embedding(cropped_face)

    # Match with database
    recognized_student = "Unknown"
    max_similarity = 0

    for student in students_collection.find():
        db_embedding = np.array(student["embedding"])
        similarity = cosine_similarity([new_embedding], [db_embedding])[0][0]
        if similarity > max_similarity:
            max_similarity = similarity
            recognized_student = student["student_id"]

    if max_similarity > SIMILARITY_THRESHOLD:
        # Send attendance data to Spring Boot service
        attendance_data = {
            "studentId": recognized_student,
            "startTime": data.get("startTime"),
            "endTime": data.get("endTime"),
            "status": data.get("status", "PRESENT")
        }

        try:
            response = requests.post(
                "http://attendance-service/attendances/facedetection",
                json=attendance_data
            )
            if response.status_code == 201:
                return jsonify({"message": "Attendance recorded", "student_id": recognized_student}), 201
            else:
                return jsonify({"error": "Failed to record attendance"}), 500
        except requests.exceptions.RequestException as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"message": "No match found"}), 404

@app.route("/students/list", methods=["GET"])
def list_students():
    """Retrieve all stored students."""
    students = list(students_collection.find({}, {"_id": 0}))
    return jsonify(students), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
