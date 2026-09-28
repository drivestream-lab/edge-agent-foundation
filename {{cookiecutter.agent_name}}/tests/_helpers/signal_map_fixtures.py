"""Shared fixtures for INIT-SIGNAL-MAP-001 unit tests (W1 mock)."""

from typing import Any
from uuid import UUID

from src.models.signal_map_models import BootstrapConfiguration

TENANT_ID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
DEVICE_ID = UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")
CORRELATION_ID = UUID("cccccccc-cccc-cccc-cccc-cccccccccccc")
RELEASE_ID = UUID("dddddddd-dddd-dddd-dddd-dddddddddddd")
VARIANT_ID = UUID("eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee")


def sample_bootstrap_configuration_dict() -> dict[str, Any]:
    """PRD §3.1-shaped bootstrap configuration (multi-IS)."""
    return {
        "release_profile": "edge_ai_integration_catalog",
        "active_release": {
            "id": str(RELEASE_ID),
            "variant_id": str(VARIANT_ID),
            "version_label": "1.0.0",
            "status_type": "published",
        },
        "variant": {
            "id": str(VARIANT_ID),
            "code": "edge-ai-lab",
            "display_name": "Edge AI Lab",
            "domain_type": "edge_ai",
        },
        "edge_settings": {"site_id": "lab-1"},
        "services": [
            {
                "service_name": "ocr",
                "base_url": "http://127.0.0.1:7300",
                "endpoints": [
                    {
                        "endpoint_name": "control",
                        "role": "command",
                        "http_method": "POST",
                        "path": "/api/v1/control",
                        "parameters_schema": {
                            "type": "object",
                            "properties": {"version": {"type": "string"}},
                            "required": ["version"],
                        },
                    },
                    {
                        "endpoint_name": "metrics",
                        "role": "observe",
                        "http_method": "GET",
                        "path": "/metrics",
                        "interval_seconds": 30,
                    },
                ],
            },
            {
                "service_name": "vision",
                "base_url": "http://127.0.0.1:7400",
                "endpoints": [
                    {
                        "endpoint_name": "status",
                        "role": "command",
                        "http_method": "GET",
                        "path": "/api/v1/status",
                    },
                ],
            },
        ],
    }


def sample_bootstrap_configuration() -> BootstrapConfiguration:
    return BootstrapConfiguration.model_validate(sample_bootstrap_configuration_dict())


def sample_autrio_command_dict(
    *,
    service_name: str = "ocr",
    endpoint_name: str = "control",
    parameters: dict[str, Any] | None = None,
    identity: str = "autrio.command.v1",
    command_type: str | None = None,
) -> dict[str, Any]:
    """PRD §3.2-shaped Autrio downlink (Edge pack with service_name/endpoint_name)."""
    return {
        "identity": identity,
        "correlation_id": str(CORRELATION_ID),
        "tenant_id": str(TENANT_ID),
        "device_id": str(DEVICE_ID),
        "topic": "devices/lab/edge_command",
        "command_type": command_type or f"{service_name}.{endpoint_name}",
        "pack": {
            "identity": "edge_ai.command.v1",
            "payload": {
                "service_name": service_name,
                "endpoint_name": endpoint_name,
                "parameters": parameters if parameters is not None else {"version": "v3"},
            },
        },
        "exp": 1735689600,
    }
