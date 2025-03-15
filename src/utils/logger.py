import os
import sys
import logging
import datetime
from logging.handlers import RotatingFileHandler


def configure_logging(log_level=logging.INFO, log_to_file=True, log_dir="logs"):
    """
    Configure logging for the application.

    Args:
        log_level (int): Logging level (e.g., logging.INFO)
        log_to_file (bool): Whether to log to file
        log_dir (str): Directory for log files
    """
    # Create logs directory if it doesn't exist
    if log_to_file and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers to avoid duplicates
    if root_logger.handlers:
        for handler in root_logger.handlers:
            root_logger.removeHandler(handler)

    # Console handler with color formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    # Create a more detailed formatter for the console
    console_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    console_formatter = logging.Formatter(console_format)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # File handler (if enabled)
    if log_to_file:
        # Create a timestamped log file name
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"pipeline_{timestamp}.log")

        # Use a rotating file handler to avoid huge log files
        file_handler = RotatingFileHandler(
            log_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
        )
        file_handler.setLevel(log_level)

        # More detailed format for file logs
        file_format = '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        file_formatter = logging.Formatter(file_format)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

    # Add custom emoji to logging levels for visibility
    logging._levelToName[logging.CRITICAL] = '🔥 CRITICAL'
    logging._levelToName[logging.ERROR] = '❌ ERROR'
    logging._levelToName[logging.WARNING] = '⚠️ WARNING'
    logging._levelToName[logging.INFO] = 'ℹ️ INFO'
    logging._levelToName[logging.DEBUG] = '🐞 DEBUG'

    return root_logger
