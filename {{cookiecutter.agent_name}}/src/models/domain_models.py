"""Domain models for {{ cookiecutter.agent_name }}."""

from enum import Enum

from pydantic import BaseModel, Field


class MilestoneType(str, Enum):
    """Closed enum for OTA reconciliation milestones."""

    STAGED = "staged"
    SHADOW_RUNNING = "shadow-running"
    PROMOTED = "promoted"
    REVERTED = "reverted"
    FAILED = "failed"


class DesiredState(BaseModel):
    """Cloud-published desired deployment state."""

    manifest_url: str
    manifest_version: str
    model_version: str
    slot_id: str = Field(default="default")


class DeviceState(BaseModel):
    """Observed on-device deployment state."""

    active_model_version: str | None = None
    staged_model_version: str | None = None
    last_milestone: MilestoneType | None = None
    engine_healthy: bool = False


class ManifestArtifact(BaseModel):
    """Single artifact entry in a deployment manifest."""

    name: str
    digest_sha256: str
    size_bytes: int
    download_url: str


class DeploymentManifest(BaseModel):
    """Signed deployment manifest (hash verify stub; TUF signature TODO)."""

    version: str
    model_version: str
    slot_id: str
    artifacts: list[ManifestArtifact]
    signature: str | None = Field(
        default=None, description="TUF signature — verify not yet implemented"
    )
