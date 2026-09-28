"""Logging package for {{ cookiecutter.agent_name }}."""

from src.logging.logging_setup import get_logger, setup_logging

__all__ = [
    "get_logger",
    "setup_logging",
]
