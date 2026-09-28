"""Unit tests for settings."""

from src.configs.app_settings import AppSettings, Environment
from src.configs.host_supervisor_settings import HostSupervisorSettings


def test_app_settings_defaults():
    settings = AppSettings()
    assert settings.environment == Environment.DEVELOPMENT
    assert settings.device_id
    assert settings.log_level == "INFO"


def test_host_supervisor_settings_from_env(monkeypatch):
    monkeypatch.setenv("HOST_SUPERVISOR_ENDPOINT", "unix:///tmp/test-supervisor.sock")
    monkeypatch.setenv("HOST_SUPERVISOR_ENABLED", "false")
    settings = HostSupervisorSettings()
    assert settings.endpoint == "unix:///tmp/test-supervisor.sock"
    assert settings.enabled is False
