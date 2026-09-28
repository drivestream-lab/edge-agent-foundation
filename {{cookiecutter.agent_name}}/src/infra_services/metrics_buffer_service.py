"""Observability metrics buffer — SQLite WAL, loss-tolerant lane."""

import json
import time
from dataclasses import dataclass

import aiosqlite
from injector import inject

from src.configs.buffer_settings import BufferSettings
from src.exceptions import BufferError
from src.infra_services.base_infra_service import BaseInfraService
from src.logging import get_logger
from src.utils.hash_utils import ensure_dir

logger = get_logger()


@dataclass
class MetricRecord:
    """Single metrics scrape record."""

    id: int
    metric_name: str
    value: float
    labels: dict[str, str]
    scraped_at: float


class MetricsBufferService(BaseInfraService):
    """Disk-backed metrics buffer with SQLite WAL mode."""

    @inject
    def __init__(self, settings: BufferSettings) -> None:
        super().__init__()
        self._settings = settings
        self._db_path = ensure_dir(settings.data_dir) / "metrics.db"
        self._max_rows = settings.metrics_max_rows
        self._conn: aiosqlite.Connection | None = None

    async def initialize(self) -> None:
        self._conn = await aiosqlite.connect(self._db_path)
        await self._conn.execute("PRAGMA journal_mode=WAL")
        await self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                value REAL NOT NULL,
                labels_json TEXT NOT NULL DEFAULT '{}',
                scraped_at REAL NOT NULL
            )
            """
        )
        await self._conn.commit()
        self._initialized = True
        logger.info("MetricsBufferService initialized", path=str(self._db_path))

    async def write(
        self, metric_name: str, value: float, labels: dict[str, str] | None = None
    ) -> int:
        if self._conn is None:
            raise BufferError("MetricsBufferService not initialized")
        labels_json = json.dumps(labels or {})
        scraped_at = time.time()
        cursor = await self._conn.execute(
            "INSERT INTO metrics (metric_name, value, labels_json, scraped_at) VALUES (?, ?, ?, ?)",
            (metric_name, value, labels_json, scraped_at),
        )
        await self._conn.commit()
        row_id = cursor.lastrowid or 0
        await self._evict_if_needed()
        return row_id

    async def read_batch(self, limit: int = 100) -> list[MetricRecord]:
        if self._conn is None:
            raise BufferError("MetricsBufferService not initialized")
        cursor = await self._conn.execute(
            "SELECT id, metric_name, value, labels_json, scraped_at FROM metrics ORDER BY id ASC LIMIT ?",
            (limit,),
        )
        rows = await cursor.fetchall()
        return [
            MetricRecord(
                id=row[0],
                metric_name=row[1],
                value=row[2],
                labels=json.loads(row[3]),
                scraped_at=row[4],
            )
            for row in rows
        ]

    async def delete_through(self, last_id: int) -> None:
        if self._conn is None:
            raise BufferError("MetricsBufferService not initialized")
        await self._conn.execute("DELETE FROM metrics WHERE id <= ?", (last_id,))
        await self._conn.commit()

    async def count(self) -> int:
        if self._conn is None:
            raise BufferError("MetricsBufferService not initialized")
        cursor = await self._conn.execute("SELECT COUNT(*) FROM metrics")
        row = await cursor.fetchone()
        return int(row[0]) if row else 0

    async def _evict_if_needed(self) -> None:
        if self._conn is None:
            return
        count = await self.count()
        if count <= self._max_rows:
            return
        overflow = count - self._max_rows
        await self._conn.execute(
            """
            DELETE FROM metrics WHERE id IN (
                SELECT id FROM metrics ORDER BY scraped_at ASC LIMIT ?
            )
            """,
            (overflow,),
        )
        await self._conn.commit()
        logger.debug("MetricsBufferService evicted old rows", count=overflow)

    async def close(self) -> None:
        if self._conn is not None:
            await self._conn.close()
            self._conn = None
        self._initialized = False

    async def health_check(self) -> bool:
        return self._initialized and self._conn is not None
