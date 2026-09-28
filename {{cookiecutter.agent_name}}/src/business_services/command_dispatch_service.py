"""Autrio command dispatch against bootstrap inventory (INIT-SIGNAL-MAP-001)."""

from typing import Any

import httpx
from injector import inject
from pydantic import ValidationError

from src.business_services.base_business_service import BaseBusinessService
from src.business_services.bootstrap_inventory_service import BootstrapInventoryService
from src.exceptions import (
    InventoryLookupError,
    UnsupportedCommandIdentityError,
)
from src.infra_services.inventory_http_client_service import InventoryHttpClientService
from src.logging import get_logger
from src.models.signal_map_models import (
    AutrioCommandEnvelope,
    AutrioCommandResponseEnvelope,
    AutrioCommandResponsePack,
    CommandResponseStatusType,
    EndpointRoleType,
)

logger = get_logger()

_AUTRIO_COMMAND_IDENTITY = "autrio.command.v1"
_AUTRIO_RESPONSE_IDENTITY = "autrio.command_response.v1"


class CommandDispatchService(BaseBusinessService):
    """
    Validate Autrio downlink → inventory lookup → local HTTP → uplink statuses.

    Non-``autrio.command.v1`` identities are rejected (D12). Host/URL are never
    taken from the Autrio pack (D9 / REQ-07).
    """

    @inject
    def __init__(
        self,
        inventory: BootstrapInventoryService,
        http_client: InventoryHttpClientService,
    ) -> None:
        super().__init__()
        self._inventory = inventory
        self._http_client = http_client

    def parse_downlink(self, raw: dict[str, Any]) -> AutrioCommandEnvelope:
        """
        Validate downlink JSON as ``autrio.command.v1``.

        Raises ``UnsupportedCommandIdentityError`` for any other identity (D12).
        """
        identity = raw.get("identity")
        if identity != _AUTRIO_COMMAND_IDENTITY:
            raise UnsupportedCommandIdentityError(
                f"rejected non-autrio command identity: {identity!r}"
            )
        try:
            return AutrioCommandEnvelope.model_validate(raw)
        except ValidationError as exc:
            raise UnsupportedCommandIdentityError(
                f"invalid autrio.command.v1 envelope: {exc}"
            ) from exc

    async def dispatch(self, raw: dict[str, Any]) -> list[AutrioCommandResponseEnvelope]:
        """
        Execute one Autrio downlink.

        Returns uplink envelopes in order: ``acked``, then ``executed`` or
        ``failed``.
        """
        command = self.parse_downlink(raw)
        responses: list[AutrioCommandResponseEnvelope] = [
            self._build_response(
                command,
                CommandResponseStatusType.ACKED,
                result={"phase": "acked"},
            )
        ]

        payload = command.pack.payload
        try:
            resolved = self._inventory.lookup(payload.service_name, payload.endpoint_name)
        except InventoryLookupError as exc:
            logger.warning(
                "Command inventory lookup failed",
                correlation_id=str(command.correlation_id),
                service_name=payload.service_name,
                endpoint_name=payload.endpoint_name,
            )
            responses.append(
                self._build_response(
                    command,
                    CommandResponseStatusType.FAILED,
                    result={"error": str(exc), "phase": "lookup"},
                )
            )
            return responses

        if resolved.role != EndpointRoleType.COMMAND:
            msg = (
                f"endpoint ({payload.service_name}, {payload.endpoint_name}) "
                f"has role={resolved.role.value}; command dispatch requires command"
            )
            logger.warning(
                "Command dispatch refused non-command endpoint",
                correlation_id=str(command.correlation_id),
                service_name=payload.service_name,
                endpoint_name=payload.endpoint_name,
                role=resolved.role.value,
            )
            responses.append(
                self._build_response(
                    command,
                    CommandResponseStatusType.FAILED,
                    result={"error": msg, "phase": "role"},
                )
            )
            return responses

        try:
            http_response = await self._http_client.request(
                resolved.http_method,
                resolved.url,
                payload.parameters,
            )
            http_response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.warning(
                "Command HTTP call failed",
                correlation_id=str(command.correlation_id),
                url=resolved.url,
                method=resolved.http_method.value,
                error=str(exc),
            )
            responses.append(
                self._build_response(
                    command,
                    CommandResponseStatusType.FAILED,
                    result={
                        "error": str(exc),
                        "phase": "http",
                        "url": resolved.url,
                        "http_method": resolved.http_method.value,
                    },
                )
            )
            return responses

        body: Any
        try:
            body = http_response.json()
        except ValueError:
            body = {"text": http_response.text}

        logger.info(
            "Command executed",
            correlation_id=str(command.correlation_id),
            service_name=payload.service_name,
            endpoint_name=payload.endpoint_name,
            status_code=http_response.status_code,
        )
        responses.append(
            self._build_response(
                command,
                CommandResponseStatusType.EXECUTED,
                result={
                    "phase": "executed",
                    "status_code": http_response.status_code,
                    "body": body if isinstance(body, dict) else {"value": body},
                },
            )
        )
        return responses

    def _build_response(
        self,
        command: AutrioCommandEnvelope,
        status: CommandResponseStatusType,
        result: dict[str, Any],
    ) -> AutrioCommandResponseEnvelope:
        return AutrioCommandResponseEnvelope(
            identity=_AUTRIO_RESPONSE_IDENTITY,
            correlation_id=command.correlation_id,
            tenant_id=command.tenant_id,
            device_id=command.device_id,
            status=status,
            pack=AutrioCommandResponsePack(
                identity=command.pack.identity,
                result=result,
            ),
        )
