"""Telemetry forward orchestrator for {{ cookiecutter.agent_name }}."""

from injector import inject

from src.business_services.base_business_service import BaseBusinessService
from src.infra_services.host_supervisor_client_service import HostSupervisorClientService
from src.infra_services.metrics_buffer_service import MetricsBufferService
from src.infra_services.scrape_client_service import ScrapeClientService
from src.logging import get_logger

logger = get_logger()


class TelemetryForwardService(BaseBusinessService):
    """Thin orchestrator: scrape metrics, buffer, publish toward host supervisor."""

    @inject
    def __init__(
        self,
        scrape_client: ScrapeClientService,
        metrics_buffer: MetricsBufferService,
        host_supervisor: HostSupervisorClientService,
    ) -> None:
        super().__init__()
        self._scrape_client = scrape_client
        self._metrics_buffer = metrics_buffer
        self._host_supervisor = host_supervisor

    async def scrape_and_buffer_once(self) -> int:
        """Scrape once via ScrapeClientService (writes into MetricsBufferService)."""
        written = await self._scrape_client.scrape_once()
        logger.debug(
            "Telemetry scrape-and-buffer complete",
            samples=written,
            buffered=await self._metrics_buffer.count(),
        )
        return written

    async def flush_batch_to_supervisor(self, limit: int = 100) -> int:
        """Publish a buffered metrics batch to the host supervisor (stub path)."""
        batch = await self._metrics_buffer.read_batch(limit=limit)
        if not batch:
            return 0
        await self._host_supervisor.publish(
            "telemetry.metrics",
            {
                "count": len(batch),
                "ids": [r.id for r in batch],
            },
        )
        last_id = batch[-1].id
        await self._metrics_buffer.delete_through(last_id)
        return len(batch)
