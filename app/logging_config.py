"""Centralized logging configuration."""
import logging
import os
from logging.handlers import RotatingFileHandler


def configure_logging(app):
    log_level = getattr(logging, app.config.get("LOG_LEVEL", "INFO").upper(), logging.INFO)
    log_file = app.config.get("LOG_FILE")

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    if not any(isinstance(h, logging.StreamHandler) for h in root_logger.handlers):
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        root_logger.addHandler(stream_handler)

    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        if not any(isinstance(h, RotatingFileHandler) for h in root_logger.handlers):
            file_handler = RotatingFileHandler(log_file, maxBytes=2_000_000, backupCount=5)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)

    logging.getLogger("apscheduler").setLevel(logging.WARNING)
    logging.getLogger("werkzeug").setLevel(logging.WARNING)
