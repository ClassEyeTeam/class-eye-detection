
from flask import Blueprint
from .student_routes import student_bp

def register_routes(app):
    app.register_blueprint(student_bp)