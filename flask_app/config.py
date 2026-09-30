"""Application configuration loaded from the local environment."""

import os


SECRET_KEY = os.getenv("SECRET_KEY")
MONGODB_HOST = os.getenv("MONGODB_URI")
