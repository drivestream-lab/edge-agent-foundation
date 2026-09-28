"""Local inventory HTTP client for on-device Intelligent Services."""

from typing import Any

import httpx
from injector import inject

from src.infra_services.base_infra_service import BaseInfraService
from src.logging import get_logger
from src.models.signal_map_models import HttpMethodType

logger = get_logger()


class InventoryHttpClientService(BaseInfraService):
    """HTTP client for bootstrap inventory URLs — D8 parameter binding."""

    @inject
    def __init__(self) -> None:
        super().__init__()
        self._client: httpx.AsyncClient | None = None

    async def initialize(self) -> None:
        self._client = httpx.AsyncClient(timeout=30.0)
        self._initialized = True
        self.logger.info("InventoryHttpClientService initialized")

    async def request(
        self,
        method: HttpMethodType,
        url: str,
        parameters: dict[str, Any],
    ) -> httpx.Response:
        """
        Call ``url`` with catalog ``http_method``.

        GET/DELETE → query string; POST/PUT/PATCH → JSON body (D8).
        """
        if self._client is None:
            raise RuntimeError("InventoryHttpClientService not initialized")

        method_value = method.value
        if method in (HttpMethodType.GET, HttpMethodType.DELETE):
            response = await self._client.request(method_value, url, params=parameters or None)
        elif method in (
            HttpMethodType.POST,
            HttpMethodType.PUT,
            HttpMethodType.PATCH,
        ):
            response = await self._client.request(method_value, url, json=parameters)
        else:
            raise ValueError(f"unsupported http_method: {method_value}")

        logger.debug(
            "Inventory HTTP request complete",
            method=method_value,
            url=url,
            status_code=response.status_code,
        )
        return response

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None
        self._initialized = False

    async def health_check(self) -> bool:
        return self._initialized and self._client is not None
