
from pymongo import MongoClient

def init_db(app):
    client = MongoClient("mongodb://localhost:27017")
    app.db = client["attendance_db"]