"""
Application configuration.
Reads sensible defaults; override via environment variables in production.
"""
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Secret key used to sign session cookies / CSRF tokens
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

    # SQLite database stored inside /database
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'database', 'inventory.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Uploaded product images
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "images", "products")
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB max upload

    # Business rules
    LOW_STOCK_THRESHOLD = 10  # quantity at/below this is "low stock"

    # Pagination
    ITEMS_PER_PAGE = 10
