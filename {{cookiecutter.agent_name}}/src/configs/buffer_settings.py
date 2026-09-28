"""Buffer and scrape settings for {{ cookiecutter.agent_name }}."""

from pydantic import Field
from pydantic_settings import SettingsConfigDict

from src.configs.base_settings import BaseSettings


class BufferSettings(BaseSettings):
    """Disk-backed buffer configuration."""

    model_config = SettingsConfigDict(
        env_prefix="BUFFER_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    data_dir: str = Field(default="data/buffers")
    metrics_max_rows: int = Field(default=10000)
    capture_max_rows: int = Field(default=1000)


class ScrapeSettings(BaseSettings):
    """Prometheus scrape configuration."""

    model_config = SettingsConfigDict(
        env_prefix="SCRAPE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    endpoint: str = Field(default="http://localhost:8002/metrics")
    interval_seconds: int = Field(default=30)


class EngineSettings(BaseSettings):
    """Inference engine container configuration."""

    model_config = SettingsConfigDict(
        env_prefix="ENGINE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    container_name: str = Field(default="inference-engine")
    image: str = Field(default="inference-engine:latest")
    enabled: bool = Field(default=False)
