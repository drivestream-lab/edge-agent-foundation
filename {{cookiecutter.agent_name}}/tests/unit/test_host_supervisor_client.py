"""Unit tests for HostSupervisorClientService."""

import pytest

from src.configs.host_supervisor_settings import HostSupervisorSettings
from src.infra_services.host_supervisor_client_service import HostSupervisorClientService


@pytest.mark.asyncio
async def test_publish_records_when_enabled():
    settings = HostSupervisorSettings(enabled=True, endpoint="unix:///tmp/x.sock")
    svc = HostSupervisorClientService(settings)
    await svc.initialize()
    await svc.publish("telemetry.metrics", {"count": 1})
    assert len(svc.published_records()) == 1
    assert svc.published_records()[0]["channel"] == "telemetry.metrics"
    await svc.close()


@pytest.mark.asyncio
async def test_publish_skipped_when_disabled():
    settings = HostSupervisorSettings(enabled=False)
    svc = HostSupervisorClientService(settings)
    await svc.initialize()
    await svc.publish("telemetry.metrics", {"count": 1})
    assert svc.published_records() == []
    await svc.close()
