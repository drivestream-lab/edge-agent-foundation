"""Unit tests for inventory HTTP parameter binding (D8)."""

import httpx
import pytest

from src.infra_services.inventory_http_client_service import InventoryHttpClientService
from src.models.signal_map_models import HttpMethodType


@pytest.mark.asyncio
async def test_get_binds_parameters_as_query_string():
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["method"] = request.method
        captured["url"] = str(request.url)
        return httpx.Response(200, json={"ok": True})

    client = InventoryHttpClientService()
    client._client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    client._initialized = True

    response = await client.request(
        HttpMethodType.GET,
        "http://127.0.0.1:7400/api/v1/status",
        {"detail": "full"},
    )
    assert response.status_code == 200
    assert captured["method"] == "GET"
    assert "detail=full" in str(captured["url"])

    await client.close()


@pytest.mark.asyncio
async def test_post_binds_parameters_as_json_body():
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["method"] = request.method
        captured["body"] = request.content
        return httpx.Response(200, json={"ok": True})

    client = InventoryHttpClientService()
    client._client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    client._initialized = True

    response = await client.request(
        HttpMethodType.POST,
        "http://127.0.0.1:7300/api/v1/control",
        {"version": "v3"},
    )
    assert response.status_code == 200
    assert captured["method"] == "POST"
    body = captured["body"]
    assert isinstance(body, bytes)
    assert b'"version":"v3"' in body or b'"version": "v3"' in body

    await client.close()
