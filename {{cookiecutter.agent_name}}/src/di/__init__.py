"""DI package for {{ cookiecutter.agent_name }}."""

from src.di.dependency_container import (
    close_all_services,
    configure_container,
    get_container,
    initialize_all_services,
    provide_service,
    reset_container,
)

__all__ = [
    "close_all_services",
    "configure_container",
    "get_container",
    "initialize_all_services",
    "provide_service",
    "reset_container",
]
