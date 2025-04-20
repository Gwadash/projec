from flask import Flask
from app.routes import main_bp
import os

def create_app():
    app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), 'templates')
    )

    app.secret_key = "super_secret_key_12345"

    app.register_blueprint(main_bp, url_prefix="/")

    return app