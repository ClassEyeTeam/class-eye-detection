
from flask import Flask
from .database import init_db
from .routes import register_routes


def create_app():
    """Application factory to create and configure the app."""
    app = Flask(__name__)
    app.config.from_object("config.Config")

    # Initialize database
    init_db(app)

    # Register blueprints
    register_routes(app)

    return app
