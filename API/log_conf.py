import logging
from logging.handlers import RotatingFileHandler, SMTPHandler

# create a custom logger
logger = logging.getLogger("app")

# set the logging level 
logger.setLevel(logging.DEBUG)

# format for log messages
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# console Handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)  # Log debug and above to console
console_handler.setFormatter(formatter)

# file Handler with Rotation
file_handler = RotatingFileHandler(
    "app.log", maxBytes=5 * 1024 * 1024, backupCount=3  # 5MB per file, 3 backups
)
file_handler.setLevel(logging.INFO)  # Log info and above to file
file_handler.setFormatter(formatter)

# email Notifications for errors
# Replace with your email settings
smtp_handler = SMTPHandler(
    mailhost=("smtp.your-email.com", 587),
    fromaddr="your-app@your-email.com",
    toaddrs=["admin@your-email.com"],
    subject="Application Critical Error",
    credentials=("your-email", "your-password"),
    secure=()
)
smtp_handler.setLevel(logging.ERROR) 
smtp_handler.setFormatter(formatter)

# add handlers to the logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)
logger.addHandler(smtp_handler)

# example usage in your application
if __name__ == "__main__":
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
