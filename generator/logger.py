from __future__ import annotations

import logging
from logging import Logger

from config import PROCESS_LOG_FILE, ensure_directories


def get_logger() -> Logger:
    ensure_directories()
    logger = logging.getLogger("attendance_star_schema")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if not logger.handlers:
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler = logging.FileHandler(PROCESS_LOG_FILE, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
