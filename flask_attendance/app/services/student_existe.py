import requests
from flask import jsonify

def record_attendance(student_id, token):
    # Format data to match Spring DTO

    try:
        response = requests.post(
            "http://localhost:8088/STUDENT-SERVICE/student/face-detection",
            json=formatted_data,
            headers={"Authorization": f"Bearer {token}"}
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
        def student_exists(student_id, token):
            try:
                response = requests.get(
                    f"http://localhost:8088/STUDENT-SERVICE/student/{student_id}",
                    headers={"Authorization": f"Bearer {token}"}
                )
                if response.status_code == 200:
                    return True
                else:
                    return False
            except requests.exceptions.RequestException as e:
                return False

        if not student_exists(student_id, token):
            return jsonify({"error": "Student does not exist"}), 404