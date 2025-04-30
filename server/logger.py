import logging
import colorlog
from datetime import datetime
import os

# Create a logs directory if it doesn't exist
log_dir = "logs/server/"
os.makedirs(log_dir, exist_ok=True)

# Generate a unique log file name with a timestamp
log_file = os.path.join(log_dir, f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

# Create a logger
logger = logging.getLogger("my_logger")
logger.setLevel(logging.DEBUG)

# Create a file handler
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.INFO)

# Create a stream handler (console output)
console_handler = logging.StreamHandler()

# Define log colors
log_colors = {
    "DEBUG": "cyan",
    "INFO": "green",
    "WARNING": "yellow",
    "ERROR": "red",
    "CRITICAL": "red,bg_white",
}


# Custom formatter to dynamically set message color and include file/line number
class CustomColoredFormatter(colorlog.ColoredFormatter):
    def format(self, record):
        # Dynamically set the message color based on the log level
        record.log_color = self.log_colors.get(record.levelname, "reset")
        # Include file and line number in the log message
        record.file_line = f"{record.filename}:{record.lineno}"
        return super().format(record)


# Create a formatter with dynamic colors and file/line number for the console
console_formatter = CustomColoredFormatter(
    "%(asctime)s - %(log_color)s%(levelname)-8s%(reset)s %(file_line)s - %(log_color)s%(message)s",
    datefmt=None,
    reset=True,
    log_colors=log_colors,
    secondary_log_colors={},
    style="%",
)

# Create a plain formatter for the file (no colors)
file_formatter = logging.Formatter(
    "%(asctime)s - %(levelname)-8s - %(filename)s:%(lineno)d - %(message)s"
)

# Set the formatters to the handlers
console_handler.setFormatter(console_formatter)
file_handler.setFormatter(file_formatter)

# Add both handlers to the logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)
