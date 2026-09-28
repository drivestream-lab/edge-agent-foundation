"""Desired-state OTA reconciliation for {{ cookiecutter.agent_name }}."""

from injector import inject

from src.business_services.base_business_service import BaseBusinessService
from src.configs.app_settings import AppSettings
from src.infra_services.engine_runtime_service import EngineRuntimeService
from src.infra_services.manifest_verifier_service import ManifestVerifierService
from src.logging import get_logger
from src.models import DesiredState, DeviceState, MilestoneType

logger = get_logger()


class ReconcileService(BaseBusinessService):
    """
    Compare desired vs actual deployment state and converge.

    The agent delivers, observes, and reports — it never switches models inside
    the engine. Day-one bootstrap with empty hosted_models is the same path.
    """

    @inject
    def __init__(
        self,
        manifest_verifier: ManifestVerifierService,
        engine_runtime: EngineRuntimeService,
    ) -> None:
        super().__init__()
        self._app_settings = AppSettings.get_instance()
        self._manifest_verifier = manifest_verifier
        self._engine_runtime = engine_runtime
        self._desired: DesiredState | None = None
        self._device_state = DeviceState()

    @property
    def device_state(self) -> DeviceState:
        return self._device_state

    def set_desired_state(self, desired: DesiredState) -> None:
        self._desired = desired
        logger.info(
            "Desired state updated",
            device_id=self._app_settings.device_id,
            model_version=desired.model_version,
        )

    async def reconcile(self) -> MilestoneType | None:
        """Run one reconciliation cycle. Returns milestone if state changed."""
        if self._desired is None:
            logger.debug("No desired state — bootstrap idle")
            return None

        manifest = await self._manifest_verifier.fetch_and_verify(self._desired.manifest_url)
        self._manifest_verifier.verify_artifact_hashes(manifest)

        self._device_state.staged_model_version = manifest.model_version
        self._device_state.last_milestone = MilestoneType.STAGED
        logger.info("Reconcile: staged", model_version=manifest.model_version)

        engine_healthy = await self._engine_runtime.health_check()
        self._device_state.engine_healthy = engine_healthy

        active_version = await self._engine_runtime.get_active_model_version()
        self._device_state.active_model_version = active_version

        if active_version == manifest.model_version:
            self._device_state.last_milestone = MilestoneType.PROMOTED
            logger.info("Reconcile: promoted", model_version=active_version)
            return MilestoneType.PROMOTED

        if engine_healthy and active_version is None:
            self._device_state.last_milestone = MilestoneType.SHADOW_RUNNING
            logger.info("Reconcile: shadow-running", model_version=manifest.model_version)
            return MilestoneType.SHADOW_RUNNING

        return self._device_state.last_milestone
