# 3rd-party packages
from flask import Flask, render_template
from flask_mongoengine import MongoEngine
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
import os

# local
from .client import StockClient

load_dotenv()

TWELVE_DATA_API_KEY = os.getenv("TWELVE_DATA_API_KEY")

db = MongoEngine()
login_manager = LoginManager()
bcrypt = Bcrypt()
stock_client = StockClient(TWELVE_DATA_API_KEY)

from .users.routes import users
from .stocks.routes import stocks

def custom_404(e):
    return render_template("404.html"), 404


def create_app(test_config=None):
    app = Flask(__name__)

    app.config.from_pyfile("config.py", silent=False)
    app.config["TWELVE_DATA_API_KEY"] = TWELVE_DATA_API_KEY
    if test_config is not None:
        app.config.update(test_config)

    required_settings = ("SECRET_KEY", "MONGODB_HOST", "TWELVE_DATA_API_KEY")
    missing_settings = [
        setting for setting in required_settings
        if not app.config.get(setting)
    ]
    if missing_settings:
        settings = ", ".join(missing_settings)
        raise RuntimeError(
            f"Missing required environment variables: {settings}. "
            "Copy .env.example to .env and provide values before starting the app."
        )

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    app.register_blueprint(users)
    app.register_blueprint(stocks)
    app.register_error_handler(404, custom_404)

    login_manager.login_view = "users.login"

    return app
