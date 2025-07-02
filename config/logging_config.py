import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    """Setup logging with rotation to prevent large log files"""
    handler = RotatingFileHandler("client.log", maxBytes=10*1024*1024, backupCount=3)
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    return logger
