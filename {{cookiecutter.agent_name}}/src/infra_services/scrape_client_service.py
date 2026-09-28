"""Prometheus metrics scrape client for {{ cookiecutter.agent_name }}."""

import re

import httpx
from injector import inject

from src.configs.buffer_settings import ScrapeSettings
from src.infra_services.base_infra_service import BaseInfraService
from src.infra_services.metrics_buffer_service import MetricsBufferService
from src.logging import get_logger

logger = get_logger()

_METRIC_LINE = re.compile(r"^([a-zA-Z_:][a-zA-Z0-9_:]*)(?:\{([^}]*)\})?\s+([-+eE0-9.]+)$")


class ScrapeClientService(BaseInfraService):
    """HTTP Prometheus scrape stub — parses text exposition into metrics buffer."""

    @inject
    def __init__(self, settings: ScrapeSettings, metrics_buffer: MetricsBufferService) -> None:
        super().__init__()
        self._settings = settings
        self._metrics_buffer = metrics_buffer
        self._client: httpx.AsyncClient | None = None

    async def initialize(self) -> None:
        self._client = httpx.AsyncClient(timeout=10.0)
        self._initialized = True
        self.logger.info("ScrapeClientService initialized", endpoint=self._settings.endpoint)

    async def scrape_once(self) -> int:
        """Fetch metrics endpoint and write parsed samples to buffer."""
        if self._client is None:
            raise RuntimeError("ScrapeClientService not initialized")
        response = await self._client.get(self._settings.endpoint)
        response.raise_for_status()
        written = 0
        for line in response.text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            match = _METRIC_LINE.match(line)
            if not match:
                continue
            name, labels_raw, value_str = match.groups()
            labels: dict[str, str] = {}
            if labels_raw:
                for part in labels_raw.split(","):
                    if "=" in part:
                        k, v = part.split("=", 1)
                        labels[k.strip()] = v.strip().strip('"')
            await self._metrics_buffer.write(name, float(value_str), labels)
            written += 1
        logger.debug("Scrape complete", endpoint=self._settings.endpoint, samples=written)
        return written

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None
        self._initialized = False

    async def health_check(self) -> bool:
        return self._initialized and self._client is not None
