import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logger(log_file_path: str) -> logging.Logger:
    logger = logging.getLogger("aura")
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    log_dir = os.path.dirname(log_file_path)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)

    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    file_handler = RotatingFileHandler(log_file_path, maxBytes=1024 * 1024, backupCount=3, encoding="utf-8")
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger
