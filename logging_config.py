"""
Logging configuration with rotation
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from config import settings


def setup_logging():
    """
    Configure application logging with rotation

    Creates a rotating file handler that:
    - Rotates when file reaches 10 MB
    - Keeps 5 backup files
    - Total max disk usage: 60 MB
    """
    # Create logs directory
    log_file = Path(settings.log_file)
    log_file.parent.mkdir(exist_ok=True)

    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(settings.log_level)

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # File handler with rotation
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,  # Keep 5 old files
        encoding="utf-8",
    )
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))

    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.info("✅ Logging configured with rotation (10 MB max, 5 backups)")
