"""Host supervisor (Runtime API) client settings for {{ cookiecutter.agent_name }}."""

from pydantic import Field
from pydantic_settings import SettingsConfigDict

from src.configs.base_settings import BaseSettings


class HostSupervisorSettings(BaseSettings):
    """Local IPC to the host supervisor — not device-root MQTT."""

    model_config = SettingsConfigDict(
        env_prefix="HOST_SUPERVISOR_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # unix://path or http://127.0.0.1:port — product ADR chooses transport
    endpoint: str = Field(default="unix:///tmp/host-supervisor.sock")
    timeout_seconds: float = Field(default=5.0)
    enabled: bool = Field(default=True)
