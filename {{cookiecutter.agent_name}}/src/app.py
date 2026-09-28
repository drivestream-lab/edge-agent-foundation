"""Edge Agent application lifecycle for {{ cookiecutter.agent_name }}."""

import asyncio
import signal

from src.configs.app_settings import AppSettings
from src.business_services.reconcile_service import ReconcileService
from src.di.dependency_container import (
    close_all_services,
    configure_container,
    initialize_all_services,
)
from src.logging import get_logger, setup_logging

logger = get_logger()


class EdgeAgent:
    """Long-running edge agent process."""

    def __init__(self) -> None:
        self._settings = AppSettings.get_instance()
        self._running = False
        self._container = configure_container()

    async def start(self) -> None:
        logger.info(
            "Starting edge agent",
            device_id=self._settings.device_id,
            environment=str(self._settings.environment),
        )
        await initialize_all_services()
        self._running = True

        reconcile = self._container.get(ReconcileService)
        milestone = await reconcile.reconcile()
        if milestone:
            logger.info("Bootstrap reconciliation complete", milestone=str(milestone))

    async def stop(self) -> None:
        logger.info("Stopping edge agent")
        self._running = False
        await close_all_services()

    async def run_forever(self) -> None:
        await self.start()
        stop_event = asyncio.Event()

        def _handle_signal() -> None:
            stop_event.set()

        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, _handle_signal)

        logger.info("Edge agent running — press Ctrl+C to stop")
        await stop_event.wait()
        await self.stop()


def create_agent() -> EdgeAgent:
    """Factory for the edge agent application."""
    settings = AppSettings.get_instance()
    setup_logging(settings)
    return EdgeAgent()
