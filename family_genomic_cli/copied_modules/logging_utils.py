import logging
import logging.handlers
import os
from datetime import datetime

def setup_logging(log_level=logging.INFO, log_to_file=True, log_to_console=True):
    """
    Set up comprehensive logging configuration for the Genetics application.

    Args:
        log_level: Logging level (e.g., logging.DEBUG, logging.INFO)
        log_to_file: Whether to log to file
        log_to_console: Whether to log to console
    """
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    os.makedirs(logs_dir, exist_ok=True)

    # Create logger
    logger = logging.getLogger('genetics_app')
    logger.setLevel(log_level)

    # Clear existing handlers
    logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )

    # File handler with rotation
    if log_to_file:
        log_file = os.path.join(logs_dir, f'genetics_app_{datetime.now().strftime("%Y%m%d")}.log')
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=10*1024*1024, backupCount=5
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Console handler
    if log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger

def get_logger(name):
    """
    Get a logger instance for a specific module.

    Args:
        name: Name of the module (usually __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(f'genetics_app.{name}')

# Global logger instance
logger = setup_logging()