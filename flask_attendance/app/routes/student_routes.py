from flask import Blueprint, request, jsonify
from app.models import Student
import os
from app.services.face_service import process_images, recognize_face
from app.services.attendance_service import record_attendance
from app.services.group_service import process_group_photo
from app.services.student_existe import enable_face_detection

from app.services.auth_service import require_auth
from datetime import datetime  
import pytz
from werkzeug.datastructures import FileStorage
from typing import List, Tuple, Dict, Any
import logging
logger = logging.getLogger(__name__)

student_bp = Blueprint("students", __name__, url_prefix="/students")
MIN_IMAGES_REQUIRED = 3
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename: str) -> bool:
    """Check if file has allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_images(files: List[FileStorage]) -> Tuple[List[str], List[str]]:
    """
    Save uploaded images and return paths.
    Returns tuple of (successful_paths, error_messages)
    """
    saved_paths = []
    errors = []
    
    upload_folder = 'uploads'
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
        
    for file in files:
        if file and allowed_file(file.filename):
            filename = os.path.join(upload_folder, file.filename)
            try:
                file.save(filename)
                saved_paths.append(filename)
            except Exception as e:
                logger.error(f"Error saving file {file.filename}: {str(e)}")
                errors.append(f"Failed to save {file.filename}")
        else:
            errors.append(f"Invalid file type for {file.filename}")
            
    return saved_paths, errors


@student_bp.route("", methods=["GET"])
@require_auth
def list_students():
    """Get all registered students."""
    try:
        students = Student.get_all_students()
        
        # Format response
        formatted_students = [{
            "student_id": student["student_id"],
            "created_at": student.get("created_at", "").isoformat() if student.get("created_at") else None
        } for student in students]

        return jsonify({
            "total_students": len(formatted_students),
            "students": formatted_students
        }), 200

    except Exception as e:
        logger.exception(f"Error retrieving students: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
    
@student_bp.route("/add", methods=["POST"])
@require_auth
def add_student() -> Tuple[Dict[str, Any], int]:
    """
    Add a new student with multiple face images.
    Requires minimum 3 images for better face recognition.
    """
    try:
        # Validate student ID
        student_id = request.form.get('student_id')
        if not student_id:
            logger.error("Missing student_id in request")
            return jsonify({"error": "Student ID is required"}), 400

        # Validate images
        if 'images' not in request.files:
            logger.error("No images in request")
            return jsonify({"error": "Images are required"}), 400

        files = request.files.getlist('images')
        if len(files) < MIN_IMAGES_REQUIRED:
            logger.error(f"Insufficient images: {len(files)} < {MIN_IMAGES_REQUIRED}")
            return jsonify({
                "error": f"Minimum {MIN_IMAGES_REQUIRED} images required"
            }), 400

        # Save images
        image_paths, errors = save_uploaded_images(files)
        if errors:
            logger.error(f"Errors during file upload: {errors}")
            return jsonify({"errors": errors}), 400

        if len(image_paths) < MIN_IMAGES_REQUIRED:
            logger.error("Insufficient valid images after processing")
            return jsonify({
                "error": f"Minimum {MIN_IMAGES_REQUIRED} valid images required"
            }), 400

        try:
            # Process images and generate embedding
            logger.info(f"Processing images for student {student_id}")
            embedding = process_images(image_paths)
            
            # Save to database
            Student.add_student(student_id, embedding)
            logger.info(f"Successfully added student {student_id}")
            enable_face_detection(student_id, request.headers.get('Authorization').split(" ")[1])

            return jsonify({
                "message": f"Student {student_id} added successfully",
                "images_processed": len(image_paths)
            }), 201

        finally:
            # Cleanup temporary files
            for path in image_paths:
                try:
                    os.remove(path)
                except Exception as e:
                    logger.warning(f"Failed to remove temporary file {path}: {str(e)}")

    except Exception as e:
        logger.exception(f"Unexpected error while adding student: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@student_bp.route("/recognize", methods=["POST"])
@require_auth
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
    local_tz = pytz.timezone('Europe/Paris') 
    timestamp = datetime.now(local_tz).isoformat()

    attendance_data = {
        "student_id": recognized_student_id,
        "timestamp": timestamp
    }
    token = request.headers.get('Authorization').split(" ")[1]

    record_attendance(attendance_data, token)

    # Clean up the temporary image file
    os.remove(image_path)

    return jsonify({
        "student_id": recognized_student_id,
        "confidence": confidence,
        "timestamp": timestamp
    })


@student_bp.route("/recognize-group", methods=["POST"])
@require_auth
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
        local_tz = pytz.timezone('Europe/Paris') 
        timestamp = datetime.now(local_tz).isoformat()
        recognized_students, total_faces = process_group_photo(group_image_path, upload_folder)
        
        # Record attendance for recognized students
        for student in recognized_students:
            attendance_data = {
                "student_id": student["student_id"],
                "session_id": session_id,
                "timestamp": timestamp
            }
            token = request.headers.get('Authorization').split(" ")[1]
            record_attendance(attendance_data, token)

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