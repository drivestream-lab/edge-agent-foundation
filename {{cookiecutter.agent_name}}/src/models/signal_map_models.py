"""Bootstrap inventory (signal map) and Autrio command/response wire models.

INIT-SIGNAL-MAP-001 — catalog keys are ``service_name`` / ``endpoint_name`` (not UUIDs).
"""

from enum import Enum
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class HttpMethodType(str, Enum):
    """First-class HTTP methods on inventory endpoints (D6)."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


class EndpointRoleType(str, Enum):
    """Endpoint role in bootstrap inventory (D5 — observe never an RO offer)."""

    COMMAND = "command"
    OBSERVE = "observe"


class CommandResponseStatusType(str, Enum):
    """Uplink statuses allowed on autrio.command_response.v1 (D11)."""

    ACKED = "acked"
    EXECUTED = "executed"
    FAILED = "failed"


class InventoryEndpoint(BaseModel):
    """One local HTTP endpoint under a service in bootstrap configuration."""

    model_config = ConfigDict(extra="forbid")

    endpoint_name: str = Field(..., min_length=1)
    role: EndpointRoleType
    http_method: HttpMethodType
    path: str = Field(..., min_length=1)
    parameters_schema: Optional[dict[str, Any]] = Field(default=None)
    interval_seconds: Optional[int] = Field(default=None, ge=1)


class InventoryService(BaseModel):
    """One on-device HTTP service entry (multi-IS normal — D1)."""

    model_config = ConfigDict(extra="forbid")

    service_name: str = Field(..., min_length=1)
    base_url: str = Field(..., min_length=1)
    endpoints: list[InventoryEndpoint] = Field(default_factory=list)


class ActiveRelease(BaseModel):
    """Release identity from enriched_detailed resolve (D3)."""

    model_config = ConfigDict(extra="forbid")

    id: UUID
    variant_id: UUID
    version_label: str
    status_type: str


class VariantSummary(BaseModel):
    """Variant summary carried on bootstrap configuration."""

    model_config = ConfigDict(extra="forbid")

    id: UUID
    code: str
    display_name: str
    domain_type: str


class BootstrapConfiguration(BaseModel):
    """Setu bootstrap ``configuration`` — Edge signal-map inventory (D2)."""

    model_config = ConfigDict(extra="ignore")

    release_profile: Optional[str] = Field(default=None)
    active_release: Optional[ActiveRelease] = Field(default=None)
    variant: Optional[VariantSummary] = Field(default=None)
    edge_settings: Optional[dict[str, Any]] = Field(default=None)
    services: list[InventoryService] = Field(default_factory=list)


class ResolvedInventoryEndpoint(BaseModel):
    """Indexed inventory leaf keyed by (service_name, endpoint_name)."""

    model_config = ConfigDict(extra="forbid")

    service_name: str
    endpoint_name: str
    base_url: str
    role: EndpointRoleType
    http_method: HttpMethodType
    path: str
    parameters_schema: Optional[dict[str, Any]] = Field(default=None)
    interval_seconds: Optional[int] = Field(default=None)

    @property
    def url(self) -> str:
        return f"{self.base_url.rstrip('/')}{self.path}"


class ObserveScheduleEntry(BaseModel):
    """Observe-role endpoint scheduled from bootstrap inventory only (D5)."""

    model_config = ConfigDict(extra="forbid")

    service_name: str
    endpoint_name: str
    url: str
    http_method: HttpMethodType
    interval_seconds: int


class AutrioEdgeCommandPayload(BaseModel):
    """Edge AI Autrio pack payload — routing slugs only; no URL (D9)."""

    model_config = ConfigDict(extra="forbid")

    service_name: str = Field(..., min_length=1)
    endpoint_name: str = Field(..., min_length=1)
    parameters: dict[str, Any] = Field(default_factory=dict)


class AutrioCommandPack(BaseModel):
    """Nested pack inside autrio.command.v1."""

    model_config = ConfigDict(extra="forbid")

    identity: str = Field(..., min_length=1)
    payload: AutrioEdgeCommandPayload


class AutrioCommandEnvelope(BaseModel):
    """Downlink Autrio product envelope (CTR-04 / D12)."""

    model_config = ConfigDict(extra="forbid")

    identity: str = Field(..., min_length=1)
    correlation_id: UUID
    tenant_id: UUID
    device_id: UUID
    topic: str = Field(..., min_length=1)
    command_type: str = Field(..., min_length=1)
    pack: AutrioCommandPack
    exp: int = Field(..., ge=1)

    @model_validator(mode="after")
    def _require_autrio_command_identity(self) -> "AutrioCommandEnvelope":
        if self.identity != "autrio.command.v1":
            raise ValueError(
                f"unsupported command identity: {self.identity}; " "expected autrio.command.v1"
            )
        return self


class AutrioCommandResponsePack(BaseModel):
    """Nested pack inside autrio.command_response.v1."""

    model_config = ConfigDict(extra="forbid")

    identity: str = Field(..., min_length=1)
    result: dict[str, Any] = Field(default_factory=dict)


class AutrioCommandResponseEnvelope(BaseModel):
    """Uplink device-result envelope (D11) — status vocabulary locked."""

    model_config = ConfigDict(extra="forbid")

    identity: str = Field(default="autrio.command_response.v1")
    correlation_id: UUID
    tenant_id: UUID
    device_id: UUID
    status: CommandResponseStatusType
    pack: AutrioCommandResponsePack

    @model_validator(mode="after")
    def _require_response_identity(self) -> "AutrioCommandResponseEnvelope":
        if self.identity != "autrio.command_response.v1":
            raise ValueError(
                f"unsupported response identity: {self.identity}; "
                "expected autrio.command_response.v1"
            )
        return self
