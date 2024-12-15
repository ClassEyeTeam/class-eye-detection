# Face Recognition Microservice

This microservice is part of a university management system designed to handle facial recognition for student attendance. It leverages MongoDB for data storage, TensorFlow for deep learning, and DeepFace for facial recognition.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Setup and Installation](#setup-and-installation)
- [API Documentation](#api-documentation)
- [Contributing](#contributing)
- [License](#license)

## Overview
The Face Recognition Microservice is responsible for:
- Adding new students with their facial embeddings.
- Recognizing students from individual or group photos.
- Recording attendance based on facial recognition.

## Features
- **Add Student**: Register a new student with multiple face images.
- **Recognize Student**: Identify a student from an uploaded image.
- **Recognize Group**: Identify multiple students from a group photo.
- **Record Attendance**: Automatically record attendance upon successful recognition.

## Technologies Used
- **Flask**: Web framework for building the API.
- **MongoDB**: Database for storing student information and embeddings.
- **TensorFlow**: Deep learning framework used by DeepFace.
- **DeepFace**: Library for facial recognition and analysis.
- **MTCNN**: Face detection model used to locate faces in images.
- **AWS Cognito**: For authentication and authorization.

## Setup and Installation
1. **Clone the repository**:
    ```sh
    git clone https://github.com/yourusername/face-recognition-microservice.git
    cd face-recognition-microservice
    ```

2. **Create a virtual environment and activate it**:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

4. **Set up environment variables**:
    Create a `.env` file and add the following:
    ```env
    AWS_REGION=your-aws-region
    COGNITO_USER_POOL_ID=your-cognito-user-pool-id
    COGNITO_CLIENT_ID=your-cognito-client-id
    COGNITO_CLIENT_SECRET=your-cognito-client-secret
    ```

5. **Run the application**:
    ```sh
    flask run
    ```

## API Documentation

### List Students
- **Endpoint**: `GET /students`
- **Description**: Retrieve all registered students.
- **Headers**: 
  - `Authorization: Bearer <token>`
- **Response**:
    ```json
    {
        "total_students": 10,
        "students": [
            {
                "student_id": "12345",
                "created_at": "2023-10-01T12:00:00Z"
            },
            ...
        ]
    }
    ```

### Add Student
- **Endpoint**: `POST /students/add`
- **Description**: Add a new student with multiple face images.
- **Headers**: 
  - `Authorization: Bearer <token>`
- **Form Data**:
  - `student_id`: Student ID
  - `images`: List of image files
- **Response**:
    ```json
    {
        "message": "Student 12345 added successfully",
        "images_processed": 3
    }
    ```

### Recognize Student
- **Endpoint**: `POST /students/recognize`
- **Description**: Recognize a student from an uploaded image.
- **Headers**: 
  - `Authorization: Bearer <token>`
- **Form Data**:
  - `image`: Image file
- **Response**:
    ```json
    {
        "student_id": "12345",
        "confidence": 0.95,
        "timestamp": "2023-10-01T12:00:00Z"
    }
    ```

### Recognize Group
- **Endpoint**: `POST /students/recognize-group`
- **Description**: Recognize multiple students from a group photo.
- **Headers**: 
  - `Authorization: Bearer <token>`
- **Form Data**:
  - `session_id`: Session ID
  - `image`: Image file
- **Response**:
    ```json
    {
        "session_id": "session123",
        "timestamp": "2023-10-01T12:00:00Z",
        "recognized_students": [
            {
                "student_id": "12345",
                "confidence": 0.95
            },
            ...
        ],
        "total_faces_detected": 5,
        "total_students_recognized": 3
    }
    ```

## Contributing
Contributions are welcome! Please read the [contributing guidelines](CONTRIBUTING.md) first.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.