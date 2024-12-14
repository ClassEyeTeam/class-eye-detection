import requests
from flask import jsonify
from datetime import datetime

def record_attendance(attendance_data):
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
            return jsonify({
                "message": "Attendance recorded", 
                "studentId": formatted_data["studentId"]
            }), 201
        else:
            return jsonify({"error": "Failed to record attendance"}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500