"""Business services DI module for {{ cookiecutter.agent_name }}."""

from injector import Binder, Module, singleton

from src.business_services.bootstrap_inventory_service import BootstrapInventoryService
from src.business_services.command_dispatch_service import CommandDispatchService
from src.business_services.governance_service import GovernanceService
from src.business_services.reconcile_service import ReconcileService
from src.business_services.telemetry_forward_service import TelemetryForwardService


class ServicesModule(Module):
    """Bind business services as singletons."""

    def configure(self, binder: Binder) -> None:
        binder.bind(ReconcileService, scope=singleton)
        binder.bind(GovernanceService, scope=singleton)
        binder.bind(TelemetryForwardService, scope=singleton)
        binder.bind(BootstrapInventoryService, scope=singleton)
        binder.bind(CommandDispatchService, scope=singleton)
