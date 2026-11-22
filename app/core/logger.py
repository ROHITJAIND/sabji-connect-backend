"""Application-wide logging configuration."""

import logging
import sys

from app.core.config import env


def setup_logger() -> None:
    """Configure application-wide console logging."""
    logging.basicConfig(
        level=env.LOG_LEVEL.upper(),
        format=(
            "%(asctime)s | %(levelname)-8s | "
            "%(name)s:%(funcName)s:%(lineno)d - %(message)s"
        ),
        stream=sys.stdout,
        force=True,
    )


setup_logger()
logger = logging.getLogger(__name__)
