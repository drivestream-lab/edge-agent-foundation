"""Host supervisor Runtime API client stub for {{ cookiecutter.agent_name }}."""

import json
from typing import Any

from injector import inject

from src.configs.host_supervisor_settings import HostSupervisorSettings
from src.infra_services.base_infra_service import BaseInfraService
from src.logging import get_logger

logger = get_logger()


class HostSupervisorClientService(BaseInfraService):
    """
    Chassis-local client to the host supervisor (Runtime API).

    Device-root MQTT stays with the supervisor. This agent publishes/receives
    workload desired-state over local IPC only. Full schema is a product ADR.
    """

    @inject
    def __init__(self, settings: HostSupervisorSettings) -> None:
        super().__init__()
        self._settings = settings
        self._published: list[dict[str, Any]] = []

    async def initialize(self) -> None:
        self.logger.info(
            "Initializing host supervisor client",
            endpoint=self._settings.endpoint,
            enabled=self._settings.enabled,
        )
        self._initialized = True

    async def publish(self, channel: str, payload: dict[str, Any]) -> None:
        """Enqueue a publish toward the supervisor (stub: in-memory record)."""
        if not self._settings.enabled:
            self.logger.debug("Host supervisor publish skipped (disabled)", channel=channel)
            return
        record = {"channel": channel, "payload": payload}
        self._published.append(record)
        self.logger.debug(
            "Host supervisor publish recorded",
            channel=channel,
            bytes=len(json.dumps(payload)),
        )

    async def fetch_desired(self) -> dict[str, Any] | None:
        """Fetch workload desired-state from supervisor (stub: none)."""
        if not self._settings.enabled:
            return None
        return None

    def published_records(self) -> list[dict[str, Any]]:
        """Test helper — recorded publishes."""
        return list(self._published)

    async def close(self) -> None:
        self._initialized = False

    async def health_check(self) -> bool:
        return self._initialized
