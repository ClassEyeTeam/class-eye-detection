import requests
import logging
from flask import jsonify

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def record_attendance(attendance_data, token):
    # Format data to match Spring DTO
    formatted_data = {
        "studentId": int(attendance_data["student_id"]),  # Convert to Long
        "confidence": attendance_data.get("confidence", 1.0),  # Add default confidence
        "timestamp": attendance_data["timestamp"]
    }

    try:
        response = requests.post(
            "http://localhost:8088/STUDENT-SERVICE/attendances/face-detection",
            json=formatted_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 201:
            logger.info("Attendance recorded successfully for studentId: %s", formatted_data["studentId"])
            return jsonify({
                "message": "Attendance recorded", 
                "studentId": formatted_data["studentId"]
            }), 201
        else:
            logger.error("Failed to record attendance: %s", response.text)
            return jsonify({"error": "Failed to record attendance"}), 500
    except requests.exceptions.RequestException as e:
        logger.error("RequestException: %s", str(e))
        return jsonify({"error": str(e)}), 500