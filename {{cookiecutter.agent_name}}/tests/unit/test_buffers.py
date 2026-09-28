"""Unit tests for disk-backed buffers."""

import pytest

from src.configs.buffer_settings import BufferSettings
from src.infra_services.capture_buffer_service import CaptureBufferService
from src.infra_services.metrics_buffer_service import MetricsBufferService


@pytest.fixture
def buffer_settings(tmp_path):
    return BufferSettings(data_dir=str(tmp_path / "buffers"))


@pytest.mark.asyncio
async def test_metrics_buffer_write_and_read(buffer_settings):
    buffer = MetricsBufferService(buffer_settings)
    await buffer.initialize()

    row_id = await buffer.write("inference_latency_ms", 12.5, {"model": "v1"})
    assert row_id == 1

    batch = await buffer.read_batch(limit=10)
    assert len(batch) == 1
    assert batch[0].metric_name == "inference_latency_ms"
    assert batch[0].value == 12.5
    assert batch[0].labels["model"] == "v1"

    await buffer.close()


@pytest.mark.asyncio
async def test_capture_buffer_enqueue_and_dequeue(buffer_settings):
    buffer = CaptureBufferService(buffer_settings)
    await buffer.initialize()

    await buffer.enqueue("inf-001", {"output": "ok"}, priority=5)
    await buffer.enqueue("inf-002", {"output": "late"}, priority=1)

    batch = await buffer.dequeue_batch(limit=10)
    assert len(batch) == 2
    assert batch[0].inference_id == "inf-001"
    assert batch[0].priority == 5

    await buffer.ack([batch[0].id])
    remaining = await buffer.dequeue_batch(limit=10)
    assert len(remaining) == 1
    assert remaining[0].inference_id == "inf-002"

    await buffer.close()
