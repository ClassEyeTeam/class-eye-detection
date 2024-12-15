
from pymongo import MongoClient
from datetime import datetime, timezone
client = MongoClient("mongodb://localhost:27017")
db = client["attendance_db"]

class Student:
    collection = db["students"]

    @staticmethod
    def add_student(student_id, embedding):
        """Add student with embedding and image references"""
        if Student.collection.find_one({"student_id": student_id}):
            raise ValueError(f"Student ID {student_id} already exists")
        Student.collection.insert_one({
            "student_id": student_id,
            "embedding": embedding,
            "created_at": datetime.now(timezone.utc)  
        })

    @staticmethod
    def get_all_students():
        return list(Student.collection.find({}, {"_id": 0}))

    @staticmethod
    def find_all():
        return Student.collection.find()