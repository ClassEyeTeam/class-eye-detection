
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client["attendance_db"]

class Student:
    collection = db["students"]

    @staticmethod
    def add_student(student_id, embedding):
        Student.collection.insert_one({
            "student_id": student_id,
            "embedding": embedding
        })

    @staticmethod
    def get_all_students():
        return list(Student.collection.find({}, {"_id": 0}))

    @staticmethod
    def find_all():
        return Student.collection.find()