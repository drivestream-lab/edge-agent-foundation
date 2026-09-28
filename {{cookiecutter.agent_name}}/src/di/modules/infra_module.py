"""Infrastructure DI module for {{ cookiecutter.agent_name }}."""

from injector import Binder, Module, singleton

from src.infra_services.capture_buffer_service import CaptureBufferService
from src.infra_services.engine_runtime_service import EngineRuntimeService
from src.infra_services.hardware_telemetry_service import HardwareTelemetryService
from src.infra_services.host_supervisor_client_service import HostSupervisorClientService
from src.infra_services.inventory_http_client_service import InventoryHttpClientService
from src.infra_services.manifest_verifier_service import ManifestVerifierService
from src.infra_services.metrics_buffer_service import MetricsBufferService
from src.infra_services.scrape_client_service import ScrapeClientService


class InfraModule(Module):
    """Bind infrastructure services as singletons."""

    def configure(self, binder: Binder) -> None:
        binder.bind(MetricsBufferService, scope=singleton)
        binder.bind(CaptureBufferService, scope=singleton)
        binder.bind(HostSupervisorClientService, scope=singleton)
        binder.bind(ScrapeClientService, scope=singleton)
        binder.bind(ManifestVerifierService, scope=singleton)
        binder.bind(EngineRuntimeService, scope=singleton)
        binder.bind(HardwareTelemetryService, scope=singleton)
        binder.bind(InventoryHttpClientService, scope=singleton)
