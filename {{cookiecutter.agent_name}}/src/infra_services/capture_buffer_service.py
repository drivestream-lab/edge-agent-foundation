"""Capture flywheel buffer — durable disk-backed queue, loss-averse lane."""

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
class CaptureRecord:
    """Single capture record (inference input/output join)."""

    id: int
    inference_id: str
    priority: int
    payload_json: str
    created_at: float


class CaptureBufferService(BaseInfraService):
    """Durable capture queue with priority-ordered drain."""

    @inject
    def __init__(self, settings: BufferSettings) -> None:
        super().__init__()
        self._settings = settings
        self._db_path = ensure_dir(settings.data_dir) / "captures.db"
        self._max_rows = settings.capture_max_rows
        self._conn: aiosqlite.Connection | None = None

    async def initialize(self) -> None:
        self._conn = await aiosqlite.connect(self._db_path)
        await self._conn.execute("PRAGMA journal_mode=WAL")
        await self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS captures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inference_id TEXT NOT NULL,
                priority INTEGER NOT NULL DEFAULT 0,
                payload_json TEXT NOT NULL,
                created_at REAL NOT NULL
            )
            """
        )
        await self._conn.commit()
        self._initialized = True
        logger.info("CaptureBufferService initialized", path=str(self._db_path))

    async def enqueue(
        self,
        inference_id: str,
        payload: dict,
        priority: int = 0,
    ) -> int:
        if self._conn is None:
            raise BufferError("CaptureBufferService not initialized")
        payload_json = json.dumps(payload)
        created_at = time.time()
        cursor = await self._conn.execute(
            """
            INSERT INTO captures (inference_id, priority, payload_json, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (inference_id, priority, payload_json, created_at),
        )
        await self._conn.commit()
        row_id = cursor.lastrowid or 0
        await self._evict_lowest_priority_if_needed()
        return row_id

    async def dequeue_batch(self, limit: int = 10) -> list[CaptureRecord]:
        if self._conn is None:
            raise BufferError("CaptureBufferService not initialized")
        cursor = await self._conn.execute(
            """
            SELECT id, inference_id, priority, payload_json, created_at
            FROM captures
            ORDER BY priority DESC, id ASC
            LIMIT ?
            """,
            (limit,),
        )
        rows = await cursor.fetchall()
        return [
            CaptureRecord(
                id=row[0],
                inference_id=row[1],
                priority=row[2],
                payload_json=row[3],
                created_at=row[4],
            )
            for row in rows
        ]

    async def ack(self, record_ids: list[int]) -> None:
        if self._conn is None:
            raise BufferError("CaptureBufferService not initialized")
        if not record_ids:
            return
        placeholders = ",".join("?" * len(record_ids))
        await self._conn.execute(
            f"DELETE FROM captures WHERE id IN ({placeholders})",
            record_ids,
        )
        await self._conn.commit()

    async def count(self) -> int:
        if self._conn is None:
            raise BufferError("CaptureBufferService not initialized")
        cursor = await self._conn.execute("SELECT COUNT(*) FROM captures")
        row = await cursor.fetchone()
        return int(row[0]) if row else 0

    async def _evict_lowest_priority_if_needed(self) -> None:
        if self._conn is None:
            return
        count = await self.count()
        if count <= self._max_rows:
            return
        await self._conn.execute(
            """
            DELETE FROM captures WHERE id IN (
                SELECT id FROM captures
                ORDER BY priority ASC, created_at ASC
                LIMIT 1
            )
            """
        )
        await self._conn.commit()
        logger.warning("CaptureBufferService evicted lowest-priority capture under disk cap")

    async def close(self) -> None:
        if self._conn is not None:
            await self._conn.close()
            self._conn = None
        self._initialized = False

    async def health_check(self) -> bool:
        return self._initialized and self._conn is not None
