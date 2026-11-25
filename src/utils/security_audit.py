
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
LOG_DIR = PROJECT_ROOT / "logs"
LOG_FILE = LOG_DIR / "security_audit.log"

LOG_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger("insureai.security")
logger.setLevel(logging.INFO)
logger.propagate = False

if not logger.handlers:
    handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=1_000_000,
        backupCount=3,
        encoding="utf-8"
    )

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    handler.setFormatter(formatter)
    logger.addHandler(handler)


def audit_event(event: str, status: str, details: str = ""):
    safe_event = str(event)
    safe_status = str(status)
    safe_details = str(details)

    def sanitise(value: str, limit: int) -> str:
        value = "".join(
            char if char.isprintable() else " "
            for char in value
        )
        return value[:limit]

    logger.info(
        "event=%s status=%s details=%s",
        sanitise(safe_event, 50),
        sanitise(safe_status, 30),
        sanitise(safe_details, 200)
    )
