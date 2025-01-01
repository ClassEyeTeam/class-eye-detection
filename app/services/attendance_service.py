import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def record_attendance(attendance_data, token="notexiste token"):
    logger.info("Recording attendance for studentId: %s", attendance_data["student_id"])
    # Format data to match Spring DTO
    formatted_data = {
        "studentId": int(attendance_data["student_id"]),  # Convert to Long
        "confidence": attendance_data.get("confidence", 1.0),  # Add default confidence
        "timestamp": attendance_data["timestamp"]
    }

    try:
        response = requests.post(
            "http://localhost:8088/STUDENT-SERVICE/attendances/face-detection",
            json=formatted_data
            )
        if response.status_code == 201:
            logger.info("Attendance recorded successfully for studentId: %s", formatted_data["studentId"])
            return {"message": "Attendance recorded", "studentId": formatted_data["studentId"]}, 201
        else:
            logger.error("Failed to record attendance: %s", response.text)
            return {"error": "Failed to record attendance"}, 500
    except requests.exceptions.RequestException as e:
        logger.error("RequestException: %s", str(e))
        return {"error": str(e)}, 500