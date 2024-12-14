
from flask import Blueprint, request, jsonify
from ..services.face_service import detect_and_crop, extract_embedding
from ..services.attendance_service import record_attendance
from ..models import Student
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

student_bp = Blueprint('students', __name__)

SIMILARITY_THRESHOLD = 0.8

@student_bp.route("/students/add", methods=["POST"])
def add_student():
    data = request.json
    student_id = data.get("student_id")
    image_paths = data.get("images")

    if not student_id or not image_paths:
        return jsonify({"error": "Student ID and images are required"}), 400

    embeddings = []
    for path in image_paths:
        cropped_face = detect_and_crop(path)
        embedding = extract_embedding(cropped_face)
        embeddings.append(embedding)

    avg_embedding = np.mean(embeddings, axis=0).tolist()
    Student.add_student(student_id, avg_embedding)

    return jsonify({"message": f"Student {student_id} added successfully"}), 201

@student_bp.route("/students/recognize", methods=["POST"])
def recognize_student():
    data = request.json
    image_path = data.get("image_path")
    if not image_path:
        return jsonify({"error": "Image path is required"}), 400

    cropped_face = detect_and_crop(image_path)
    new_embedding = extract_embedding(cropped_face)

    recognized_student = "Unknown"
    max_similarity = 0

    for student in Student.find_all():
        db_embedding = np.array(student["embedding"])
        similarity = cosine_similarity([new_embedding], [db_embedding])[0][0]
        if similarity > max_similarity:
            max_similarity = similarity
            recognized_student = student["student_id"]

    if max_similarity > SIMILARITY_THRESHOLD:
        attendance_data = {
            "studentId": recognized_student,
            "startTime": data.get("startTime"),
            "endTime": data.get("endTime"),
            "status": data.get("status", "PRESENT")
        }
        return record_attendance(attendance_data)
    else:
        return jsonify({"message": "No match found"}), 404

@student_bp.route("/students/list", methods=["GET"])
def list_students():
    students = Student.get_all_students()
    return jsonify(students), 200