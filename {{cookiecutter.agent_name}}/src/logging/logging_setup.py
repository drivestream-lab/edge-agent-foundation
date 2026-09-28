"""Loguru logging setup for {{ cookiecutter.agent_name }}."""

import sys
from pathlib import Path
from typing import Protocol

from loguru import logger


class LoggingSettings(Protocol):
    """Minimal settings surface required to configure logging."""

    log_level: str
    log_to_console: bool
    log_dir: str


def setup_logging(settings: LoggingSettings) -> None:
    """Configure loguru sinks from application settings."""
    logger.remove()
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    if settings.log_to_console:
        logger.add(sys.stderr, level=settings.log_level, format=log_format)
    log_dir = Path(settings.log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    logger.add(
        log_dir / "agent.log",
        level=settings.log_level,
        rotation="10 MB",
        retention="7 days",
        enqueue=True,
    )


def get_logger():
    """Return the configured loguru logger."""
    return logger
