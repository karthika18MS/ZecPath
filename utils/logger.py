import logging
import os

# Create logs directory
os.makedirs("logs", exist_ok=True)

# Create a dedicated logger
logger = logging.getLogger("ZecPath")
logger.setLevel(logging.INFO)

# Remove old handlers (important when rerunning)
if logger.hasHandlers():
    logger.handlers.clear()

# Create file handler
file_handler = logging.FileHandler("logs/app.log", mode="w", encoding="utf-8")

# Set log format
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s"
)
file_handler.setFormatter(formatter)

# Attach handler
logger.addHandler(file_handler)

logger.info("Logger initialized successfully.")