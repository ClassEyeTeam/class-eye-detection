
import requests
from flask import jsonify

def record_attendance(attendance_data):
    try:
        response = requests.post(
            "http://attendance-service/attendances/facedetection",
            json=attendance_data
        )
        if response.status_code == 201:
            return jsonify({"message": "Attendance recorded", "student_id": attendance_data["studentId"]}), 201
        else:
            return jsonify({"error": "Failed to record attendance"}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500