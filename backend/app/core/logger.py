import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.core.config import settings

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

FORMAT = (
    "%(asctime)s | "
    "%(levelname)s | "
    "%(name)s:%(funcName)s:%(lineno)d | "
    "%(message)s"
)

log_level = getattr(settings, "log_level", "INFO")

logging.basicConfig(
    level=getattr(logging, str(log_level).upper(), logging.INFO),
    format=FORMAT,
    handlers=[
        logging.StreamHandler(sys.stdout),
        RotatingFileHandler(
            LOG_DIR / "tradepilot.log",
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        ),
    ],
)

logging.getLogger("uvicorn").setLevel(logging.INFO)
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

logger = logging.getLogger("tradepilot")