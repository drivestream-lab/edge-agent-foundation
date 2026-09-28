"""Hardware telemetry provider protocol, profiles, and service."""

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

import psutil

from src.configs.app_settings import AppSettings, HardwareProfileType
from src.infra_services.base_infra_service import BaseInfraService
from src.logging import get_logger

logger = get_logger()


@dataclass
class HardwareTelemetry:
    """Snapshot of device hardware telemetry."""

    cpu_percent: float
    memory_percent: float
    gpu_util_percent: float | None = None
    gpu_memory_percent: float | None = None
    temperature_celsius: float | None = None


@runtime_checkable
class HardwareTelemetryProvider(Protocol):
    """Protocol for hardware telemetry sources."""

    async def collect(self) -> HardwareTelemetry:
        """Collect a telemetry snapshot."""
        ...


class FakeHardwareProfile:
    """Deterministic fake profile for CI and local dev."""

    async def collect(self) -> HardwareTelemetry:
        return HardwareTelemetry(
            cpu_percent=psutil.cpu_percent(interval=0.1),
            memory_percent=psutil.virtual_memory().percent,
            gpu_util_percent=0.0,
            gpu_memory_percent=0.0,
            temperature_celsius=42.0,
        )


class NvmlHardwareProfile:
    """
    Jetson/NVIDIA telemetry via NVML.

    Stub: raises NotImplementedError until pynvml is wired for target hardware.
    """

    async def collect(self) -> HardwareTelemetry:
        import importlib.util

        if importlib.util.find_spec("pynvml") is None:
            raise NotImplementedError(
                "NvmlHardwareProfile requires pynvml — install on Jetson target"
            )

        raise NotImplementedError(
            "NvmlHardwareProfile.collect is not yet implemented — wire pynvml on Jetson"
        )


class HardwareTelemetryService(BaseInfraService):
    """Wraps Fake/Nvml hardware profiles selected by AppSettings."""

    def __init__(self) -> None:
        super().__init__()
        settings = AppSettings.get_instance()
        if settings.hardware_profile == HardwareProfileType.NVML:
            self._provider: HardwareTelemetryProvider = NvmlHardwareProfile()
        else:
            self._provider = FakeHardwareProfile()

    async def initialize(self) -> None:
        self._initialized = True
        self.logger.info(
            "HardwareTelemetryService initialized",
            provider=type(self._provider).__name__,
        )

    async def collect(self) -> HardwareTelemetry:
        return await self._provider.collect()

    async def close(self) -> None:
        self._initialized = False

    async def health_check(self) -> bool:
        return self._initialized
