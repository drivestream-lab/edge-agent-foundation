"""Unit tests for INIT-SIGNAL-MAP-001 bootstrap inventory + Autrio dispatch."""

from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from src.business_services.bootstrap_inventory_service import BootstrapInventoryService
from src.business_services.command_dispatch_service import CommandDispatchService
from src.exceptions import InventoryLookupError, UnsupportedCommandIdentityError
from src.models.signal_map_models import (
    AutrioCommandEnvelope,
    BootstrapConfiguration,
    CommandResponseStatusType,
    EndpointRoleType,
    HttpMethodType,
)
from tests._helpers.signal_map_fixtures import (
    CORRELATION_ID,
    sample_autrio_command_dict,
    sample_bootstrap_configuration,
    sample_bootstrap_configuration_dict,
)


def test_bootstrap_configuration_indexes_by_service_and_endpoint():
    inventory = BootstrapInventoryService()
    count = inventory.load_configuration(sample_bootstrap_configuration())

    assert count == 3
    control = inventory.lookup("ocr", "control")
    assert control.http_method == HttpMethodType.POST
    assert control.role == EndpointRoleType.COMMAND
    assert control.url == "http://127.0.0.1:7300/api/v1/control"

    metrics = inventory.lookup("ocr", "metrics")
    assert metrics.role == EndpointRoleType.OBSERVE
    assert metrics.interval_seconds == 30

    status = inventory.lookup("vision", "status")
    assert status.http_method == HttpMethodType.GET
    assert status.url == "http://127.0.0.1:7400/api/v1/status"


def test_bootstrap_lookup_miss_raises():
    inventory = BootstrapInventoryService()
    inventory.load_configuration(sample_bootstrap_configuration())

    with pytest.raises(InventoryLookupError, match="inventory miss"):
        inventory.lookup("missing", "endpoint")


def test_observe_scheduling_stub_records_observe_only():
    inventory = BootstrapInventoryService()
    inventory.load_configuration(sample_bootstrap_configuration())

    schedules = inventory.schedule_observe_endpoints()

    assert len(schedules) == 1
    assert schedules[0].service_name == "ocr"
    assert schedules[0].endpoint_name == "metrics"
    assert schedules[0].interval_seconds == 30
    assert schedules[0].url == "http://127.0.0.1:7300/metrics"
    assert inventory.observe_schedules == schedules


def test_autrio_envelope_rejects_non_autrio_identity():
    raw = sample_autrio_command_dict(identity="stratum.command.v1")
    with pytest.raises(ValueError, match="unsupported command identity"):
        AutrioCommandEnvelope.model_validate(raw)


def test_parse_downlink_rejects_non_autrio_identity():
    inventory = BootstrapInventoryService()
    dispatch = CommandDispatchService(inventory, http_client=MagicMock())
    raw = sample_autrio_command_dict(identity="stratum.command.v1")

    with pytest.raises(UnsupportedCommandIdentityError, match="rejected non-autrio"):
        dispatch.parse_downlink(raw)


@pytest.mark.asyncio
async def test_dispatch_post_uses_json_body_and_uplinks_acked_executed():
    inventory = BootstrapInventoryService()
    inventory.load_configuration(sample_bootstrap_configuration())

    http_client = MagicMock()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"ok": True}
    mock_response.raise_for_status = MagicMock()
    http_client.request = AsyncMock(return_value=mock_response)

    dispatch = CommandDispatchService(inventory, http_client)
    responses = await dispatch.dispatch(sample_autrio_command_dict())

    assert [r.status for r in responses] == [
        CommandResponseStatusType.ACKED,
        CommandResponseStatusType.EXECUTED,
    ]
    assert responses[0].correlation_id == CORRELATION_ID
    assert responses[0].identity == "autrio.command_response.v1"
    assert responses[1].pack.result["status_code"] == 200

    http_client.request.assert_awaited_once_with(
        HttpMethodType.POST,
        "http://127.0.0.1:7300/api/v1/control",
        {"version": "v3"},
    )


@pytest.mark.asyncio
async def test_dispatch_get_binds_parameters_as_query():
    inventory = BootstrapInventoryService()
    inventory.load_configuration(sample_bootstrap_configuration())

    http_client = MagicMock()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"ready": True}
    mock_response.raise_for_status = MagicMock()
    http_client.request = AsyncMock(return_value=mock_response)

    dispatch = CommandDispatchService(inventory, http_client)
    raw = sample_autrio_command_dict(
        service_name="vision",
        endpoint_name="status",
        parameters={"detail": "full"},
    )
    responses = await dispatch.dispatch(raw)

    assert responses[-1].status == CommandResponseStatusType.EXECUTED
    http_client.request.assert_awaited_once_with(
        HttpMethodType.GET,
        "http://127.0.0.1:7400/api/v1/status",
        {"detail": "full"},
    )


@pytest.mark.asyncio
async def test_dispatch_inventory_miss_uplinks_failed():
    inventory = BootstrapInventoryService()
    inventory.load_configuration(sample_bootstrap_configuration())
    http_client = MagicMock()
    http_client.request = AsyncMock()

    dispatch = CommandDispatchService(inventory, http_client)
    raw = sample_autrio_command_dict(service_name="unknown", endpoint_name="ctrl")
    responses = await dispatch.dispatch(raw)

    assert [r.status for r in responses] == [
        CommandResponseStatusType.ACKED,
        CommandResponseStatusType.FAILED,
    ]
    assert responses[1].pack.result["phase"] == "lookup"
    http_client.request.assert_not_awaited()


@pytest.mark.asyncio
async def test_dispatch_observe_endpoint_refused():
    inventory = BootstrapInventoryService()
    inventory.load_configuration(sample_bootstrap_configuration())
    http_client = MagicMock()
    http_client.request = AsyncMock()

    dispatch = CommandDispatchService(inventory, http_client)
    raw = sample_autrio_command_dict(service_name="ocr", endpoint_name="metrics")
    responses = await dispatch.dispatch(raw)

    assert responses[-1].status == CommandResponseStatusType.FAILED
    assert responses[-1].pack.result["phase"] == "role"
    http_client.request.assert_not_awaited()


@pytest.mark.asyncio
async def test_dispatch_http_error_uplinks_failed():
    inventory = BootstrapInventoryService()
    inventory.load_configuration(sample_bootstrap_configuration())

    http_client = MagicMock()
    request = httpx.Request("POST", "http://127.0.0.1:7300/api/v1/control")
    response = httpx.Response(500, request=request)
    http_client.request = AsyncMock(
        side_effect=httpx.HTTPStatusError("boom", request=request, response=response)
    )

    dispatch = CommandDispatchService(inventory, http_client)
    responses = await dispatch.dispatch(sample_autrio_command_dict())

    assert [r.status for r in responses] == [
        CommandResponseStatusType.ACKED,
        CommandResponseStatusType.FAILED,
    ]
    assert responses[1].pack.result["phase"] == "http"


def test_bootstrap_configuration_model_validate_from_dict():
    cfg = BootstrapConfiguration.model_validate(sample_bootstrap_configuration_dict())
    assert cfg.active_release is not None
    assert cfg.active_release.status_type == "published"
    assert len(cfg.services) == 2
