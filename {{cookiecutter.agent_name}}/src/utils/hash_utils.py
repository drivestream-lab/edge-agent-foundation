"""Shared utilities for {{ cookiecutter.agent_name }}."""

import hashlib
from pathlib import Path


def sha256_hex(data: bytes) -> str:
    """Return SHA-256 hex digest of bytes."""
    return hashlib.sha256(data).hexdigest()


def ensure_dir(path: str | Path) -> Path:
    """Create directory if missing and return Path."""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p
