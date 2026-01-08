"""Celery worker entry point"""
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import logger early to configure logging
import app.logger  # noqa: F401

# Import celery_app and all tasks to register them
from app.workers import celery_app

# Import all task modules to ensure they're registered
from app.tasks import (
    infrastructure,
    microservice,
    cleanup
)

if __name__ == "__main__":
    celery_app.start()
