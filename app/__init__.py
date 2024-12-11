# app/__init__.py
from flask import Flask
from config import Config


def create_app(config_class=Config):
    app = Flask(
        __name__, template_folder="../templates", static_folder="../static"
    )  # Add static folder path
    app.config.from_object(config_class)

    from app.routes import main

    app.register_blueprint(main)

    return app
