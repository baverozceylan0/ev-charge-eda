import os
import logging.config

from pathlib import Path
import pandas as pd

RAW_DATAPATH = Path.cwd() / 'data' / 'raw'
FORMATTED_DATAPATH = Path.cwd() / 'data' / 'formatted'

def setup_logger(log_file: str = "run.log", level="INFO") -> None:
    """
    Sets up a logger that prints to both the console and a file.
    Ensures consistent logging across files and subprocesses.
    """
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "level": level
            },
            "file": {
                "class": "logging.FileHandler",
                "formatter": "default",
                "level": "DEBUG",
                "filename": log_file,
            },
        },
        "root": {  # root logger
            "level": level,
            "handlers": ["console", "file"]
        },
    }

    logging.config.dictConfig(config)