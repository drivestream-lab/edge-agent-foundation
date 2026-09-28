"""Application-wide settings for {{ cookiecutter.agent_name }}."""

from enum import Enum
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import SettingsConfigDict

from src.configs.base_settings import BaseSettings

_app_instance: Optional["AppSettings"] = None


class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGE = "stage"
    TESTING = "testing"
    PRODUCTION = "production"


class HardwareProfileType(str, Enum):
    FAKE = "fake"
    NVML = "nvml"


class AppSettings(BaseSettings):
    """Application configuration settings."""

    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: Environment = Field(default=Environment.DEVELOPMENT)
    device_id: str = Field(default="dev-device-001")
    log_level: str = Field(default="INFO")
    log_format: str = Field(default="text", description="'json' in production, 'text' locally")
    log_to_console: bool = Field(default=True)
    log_dir: str = Field(default="logs")
    hardware_profile: HardwareProfileType = Field(default=HardwareProfileType.FAKE)

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        valid = ["TRACE", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid:
            raise ValueError(f"Log level must be one of {valid}")
        return v_upper

    @property
    def is_development(self) -> bool:
        return self.environment == Environment.DEVELOPMENT

    @classmethod
    def get_instance(cls) -> "AppSettings":
        global _app_instance
        if _app_instance is None:
            _app_instance = cls()
        return _app_instance
