
from flask import Flask
from .database import init_db
from .routes import register_routes

def create_app():
    app = Flask(__name__)
    init_db(app)
    register_routes(app)
    return app