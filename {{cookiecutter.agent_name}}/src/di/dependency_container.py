"""Dependency injection container for {{ cookiecutter.agent_name }}."""

from typing import Optional, Type, TypeVar

from injector import Injector

from src.configs.app_settings import AppSettings
from src.infra_services.capture_buffer_service import CaptureBufferService
from src.infra_services.engine_runtime_service import EngineRuntimeService
from src.infra_services.hardware_telemetry_service import HardwareTelemetryService
from src.infra_services.inventory_http_client_service import InventoryHttpClientService
from src.infra_services.manifest_verifier_service import ManifestVerifierService
from src.infra_services.metrics_buffer_service import MetricsBufferService
from src.infra_services.host_supervisor_client_service import HostSupervisorClientService
from src.infra_services.scrape_client_service import ScrapeClientService
from src.logging import get_logger

T = TypeVar("T")
_injector: Optional[Injector] = None
logger = get_logger()

_INFRA_INITIALIZABLE: tuple[type, ...] = (
    MetricsBufferService,
    CaptureBufferService,
    HostSupervisorClientService,
    EngineRuntimeService,
    ManifestVerifierService,
    ScrapeClientService,
    HardwareTelemetryService,
    InventoryHttpClientService,
)


def configure_container() -> Injector:
    from src.di.modules.config_module import ConfigModule
    from src.di.modules.infra_module import InfraModule
    from src.di.modules.services_module import ServicesModule

    settings = AppSettings.get_instance()
    global _injector
    if _injector is None:
        logger.info("Configuring DI container", environment=str(settings.environment))
        _injector = Injector(
            [
                ConfigModule(),
                InfraModule(),
                ServicesModule(),
            ]
        )
        logger.info("DI container configured successfully")
    return _injector


async def initialize_all_services() -> None:
    logger.info("Initializing all application services")
    injector = get_container()
    for service_type in _INFRA_INITIALIZABLE:
        service = injector.get(service_type)
        if hasattr(service, "initialize"):
            await service.initialize()
    logger.info("All application services initialized successfully")


async def close_all_services() -> None:
    logger.info("Closing all application services")
    injector = get_container()
    for service_type in reversed(_INFRA_INITIALIZABLE):
        service = injector.get(service_type)
        if hasattr(service, "close"):
            await service.close()
    logger.info("All application services closed")


def get_container() -> Injector:
    global _injector
    if _injector is None:
        raise RuntimeError("Call configure_container() first")
    return _injector


def reset_container() -> None:
    global _injector
    _injector = None


def provide_service(cls: Type[T]) -> T:
    if _injector is None:
        configure_container()
    return get_container().get(cls)
