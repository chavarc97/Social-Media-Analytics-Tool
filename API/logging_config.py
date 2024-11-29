import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    if not os.path.exists('logs'):
        os.makedirs('logs')

    file_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=10485760,  # 10MB
        backupCount=10
    )

    console_handler = logging.StreamHandler()

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

logger = setup_logger()