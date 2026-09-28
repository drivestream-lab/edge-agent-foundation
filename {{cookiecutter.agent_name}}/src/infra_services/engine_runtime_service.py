"""Inference engine container runtime stub for {{ cookiecutter.agent_name }}."""

from injector import inject

from src.configs.buffer_settings import EngineSettings
from src.infra_services.base_infra_service import BaseInfraService
from src.logging import get_logger

logger = get_logger()


class EngineRuntimeService(BaseInfraService):
    """
    Control an inference-engine container lifecycle via Docker SDK.

    Engine implementation (OCI image family) is product-chosen — chassis stays
    agnostic. No-op when Docker is unavailable or ENGINE_ENABLED=false.
    The agent observes engine state — it does not switch models internally.
    """

    @inject
    def __init__(self, settings: EngineSettings) -> None:
        super().__init__()
        self._settings = settings
        self._docker_client = None
        self._available = False

    async def initialize(self) -> None:
        if not self._settings.enabled:
            logger.info("Engine runtime disabled by settings")
            self._initialized = True
            return
        try:
            import docker

            self._docker_client = docker.from_env()  # type: ignore[attr-defined]
            self._docker_client.ping()
            self._available = True
            logger.info("Docker SDK available for engine runtime")
        except Exception as exc:
            logger.warning("Docker SDK unavailable — engine runtime no-op", error=str(exc))
            self._available = False
        self._initialized = True

    async def start(self) -> bool:
        if not self._available or self._docker_client is None:
            logger.info("Engine start skipped (docker unavailable or disabled)")
            return False
        try:
            container = self._docker_client.containers.get(self._settings.container_name)
            if container.status != "running":
                container.start()
            logger.info("Engine container started", name=self._settings.container_name)
            return True
        except Exception:
            logger.info(
                "Engine container not found — create via compose or pull image first",
                name=self._settings.container_name,
                image=self._settings.image,
            )
            return False

    async def stop(self) -> bool:
        if not self._available or self._docker_client is None:
            return False
        try:
            container = self._docker_client.containers.get(self._settings.container_name)
            container.stop(timeout=30)
            logger.info("Engine container stopped", name=self._settings.container_name)
            return True
        except Exception as exc:
            logger.warning("Engine stop failed", error=str(exc))
            return False

    async def health_check(self) -> bool:
        if not self._available or self._docker_client is None:
            return False
        try:
            container = self._docker_client.containers.get(self._settings.container_name)
            return container.status == "running"
        except Exception:
            return False

    async def get_active_model_version(self) -> str | None:
        """Observe active model version from engine metrics (stub)."""
        healthy = await self.health_check()
        if not healthy:
            return None
        return None

    async def close(self) -> None:
        if self._docker_client is not None:
            self._docker_client.close()
            self._docker_client = None
        self._initialized = False
