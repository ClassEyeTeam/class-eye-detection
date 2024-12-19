import os
from pymongo import MongoClient

def init_db(app):
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    client = MongoClient(mongo_uri)
    app.db = client["attendance_db"]