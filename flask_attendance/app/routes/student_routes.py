from flask import Blueprint, request, jsonify
from app.models import Student
import os
from app.services.face_service import process_images, recognize_face
from app.services.attendance_service import record_attendance
from datetime import datetime  # Changed this line
student_bp = Blueprint("students", __name__, url_prefix="/students")

@student_bp.route("/add", methods=["POST"])
def add_student():
    """Add a student with ID and images."""
    data = request.json
    student_id = data.get("student_id")
    images = data.get("images")  # List of image paths

    if not student_id or not images:
        return jsonify({"error": "Student ID and images are required"}), 400

    # Process images and save embedding
    embedding = process_images(images)
    Student.add_student(student_id, embedding)

    return jsonify({"message": f"Student {student_id} added successfully"}), 201


@student_bp.route("/recognize", methods=["POST"])
def recognize_student():
    """Recognize a student from an uploaded image."""
    if 'image' not in request.files:
        return jsonify({"error": "Image file is required"}), 400
    
    image = request.files['image']
    if image.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Ensure the uploads directory exists
    upload_folder = 'uploads'
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    # Save the uploaded image
    image_path = os.path.join(upload_folder, image.filename)
    image.save(image_path)

    # Recognize the student
    recognized_student_id, confidence = recognize_face(image_path)

    # Record attendance with current timestamp
    timestamp = datetime.utcnow().isoformat()
    attendance_data = {
        "student_id": recognized_student_id,
        "timestamp": timestamp
    }
    record_attendance(attendance_data)

    # Clean up the temporary image file
    os.remove(image_path)

    return jsonify({
        "student_id": recognized_student_id,
        "confidence": confidence,
        "timestamp": timestamp
    })


@student_bp.route("/recognize-group", methods=["POST"])
def recognize_group():
    """Recognize multiple students from a group photo."""
    if 'image' not in request.files:
        return jsonify({"error": "Image file is required"}), 400
    
    session_id = request.form.get('session_id')
    if not session_id:
        return jsonify({"error": "Session ID is required"}), 400

    image = request.files['image']
    if image.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Ensure uploads directory exists
    upload_folder = 'uploads'
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    # Save the uploaded image
    group_image_path = os.path.join(upload_folder, image.filename)
    image.save(group_image_path)

    try:
        timestamp = datetime.utcnow().isoformat()
        recognized_students, total_faces = process_group_photo(group_image_path, upload_folder)
        
        # Record attendance for recognized students
        for student in recognized_students:
            attendance_data = {
                "student_id": student["student_id"],
                "session_id": session_id,
                "timestamp": timestamp
            }
            record_attendance(attendance_data)

        return jsonify({
            "session_id": session_id,
            "timestamp": timestamp,
            "recognized_students": recognized_students,
            "total_faces_detected": total_faces,
            "total_students_recognized": len(recognized_students)
        }), 200

    finally:
        if os.path.exists(group_image_path):
            os.remove(group_image_path)