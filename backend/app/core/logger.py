from loguru import logger
import sys
from pathlib import Path

# Create logs directory
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Remove default logger
logger.remove()

# Console logging
logger.add(
    sys.stdout,
    level="INFO",
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
           "<level>{level}</level> | "
           "{name}:{function}:{line} - {message}"
)

# File logging
logger.add(
    LOG_DIR / "tradepilot.log",
    rotation="10 MB",
    retention="30 days",
    level="INFO",
    enqueue=True
)