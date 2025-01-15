import requests
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def enable_face_detection(student_id: str, token: str):
    """Enable face detection for a student by ID."""
    try:
        student_service_url = os.getenv("STUDENT_SERVICE_URL", "http://localhost:8088/STUDENT-SERVICE")
        response = requests.post(
            f"{student_service_url}/students/face-detection/{student_id}",
            headers={
                # "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        )
        
        if response.status_code == 200:
            logger.info(f"Face detection enabled for student ID: {student_id}")
            return {"message": "Face detection enabled", "student": response.json()}, 200
            
        elif response.status_code == 404:
            logger.error(f"Student not found with ID: {student_id}")
            return {"error": "Student not found"}, 404
            
        else:
            logger.error(f"Failed to enable face detection: {response.text}")
            return {"error": "Failed to enable face detection"}, response.status_code
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {str(e)}")
        return {"error": str(e)}, 500