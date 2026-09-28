"""Configuration DI module for {{ cookiecutter.agent_name }}."""

from injector import Module, provider, singleton

from src.configs.app_settings import AppSettings
from src.configs.buffer_settings import BufferSettings, EngineSettings, ScrapeSettings
from src.configs.host_supervisor_settings import HostSupervisorSettings


class ConfigModule(Module):
    """Provide settings singletons."""

    @singleton
    @provider
    def provide_app_settings(self) -> AppSettings:
        return AppSettings.get_instance()

    @singleton
    @provider
    def provide_host_supervisor_settings(self) -> HostSupervisorSettings:
        return HostSupervisorSettings()

    @singleton
    @provider
    def provide_buffer_settings(self) -> BufferSettings:
        return BufferSettings()

    @singleton
    @provider
    def provide_scrape_settings(self) -> ScrapeSettings:
        return ScrapeSettings()

    @singleton
    @provider
    def provide_engine_settings(self) -> EngineSettings:
        return EngineSettings()
