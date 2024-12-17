import requests
import logging
from flask import jsonify

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def enable_face_detection(student_id: str, token: str):
    """Enable face detection for a student by ID."""
    try:
        response = requests.post(
            f"http://localhost:8088/STUDENT-SERVICE/students/face-detection/{student_id}",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        )
        
        if response.status_code == 200:
            logger.info(f"Face detection enabled for student ID: {student_id}")
            return jsonify({
                "message": "Face detection enabled",
                "student": response.json()
            }), 200
            
        elif response.status_code == 404:
            logger.error(f"Student not found with ID: {student_id}")
            return jsonify({"error": "Student not found"}), 404
            
        else:
            logger.error(f"Failed to enable face detection: {response.text}")
            return jsonify({"error": "Failed to enable face detection"}), response.status_code
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {str(e)}")
        return jsonify({"error": str(e)}), 500