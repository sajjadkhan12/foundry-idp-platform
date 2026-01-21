import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from app.config import settings

# Create logs directory - use absolute path relative to backend directory
backend_dir = Path(__file__).parent.parent
log_dir = backend_dir / "logs"
log_dir.mkdir(exist_ok=True)

# Log file path
log_file = log_dir / "server.log"

# Configure root logger - remove all existing handlers first
root_logger = logging.getLogger()
root_logger.handlers = []

# Create formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Console handler for WARNING and above (reduce verbosity)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
root_logger.addHandler(console_handler)

# File handler with rotation (10MB per file, keep 5 backups)
# Only log WARNING and ERROR to server.log
file_handler = RotatingFileHandler(
    log_file,
    maxBytes=10 * 1024 * 1024,  # 10MB
    backupCount=5,
    encoding='utf-8'
)
file_handler.setLevel(logging.WARNING)  # Only WARNING and ERROR
file_handler.setFormatter(formatter)

root_logger.addHandler(file_handler)
root_logger.setLevel(logging.INFO)

# Suppress noisy loggers
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
logging.getLogger("uvicorn.error").setLevel(logging.WARNING)
# Suppress SQLAlchemy verbose query logging
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy.dialects").setLevel(logging.WARNING)
# Suppress Casbin verbose policy logging
logging.getLogger("casbin").setLevel(logging.WARNING)
logging.getLogger("casbin.policy").setLevel(logging.WARNING)
logging.getLogger("casbin.role").setLevel(logging.WARNING)
# Suppress verbose application logs
logging.getLogger("devplatform").setLevel(logging.WARNING)
logging.getLogger("app.api.v1.users").setLevel(logging.WARNING)
logging.getLogger("app.api.deps").setLevel(logging.WARNING)

# Main application logger
logger = logging.getLogger("devplatform")
# Only log initialization at DEBUG level to reduce console noise
logger.debug(f"Logging initialized. Logs will be written to: {log_file.absolute()}")
