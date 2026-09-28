"""Resource governance across hosted engines on one device."""

from dataclasses import dataclass

from injector import inject

from src.business_services.base_business_service import BaseBusinessService
from src.infra_services.hardware_telemetry_service import HardwareTelemetryService
from src.logging import get_logger

logger = get_logger()


@dataclass
class SlotQuota:
    """Resource quota for a hosted model slot."""

    slot_id: str
    max_memory_mb: int
    max_gpu_percent: float


class GovernanceService(BaseBusinessService):
    """Quota check stub — refuse or defer when headroom insufficient."""

    @inject
    def __init__(self, hardware_telemetry: HardwareTelemetryService) -> None:
        super().__init__()
        self._hardware = hardware_telemetry

    async def check_quota(self, quota: SlotQuota) -> bool:
        telemetry = await self._hardware.collect()
        if telemetry.memory_percent > 90.0:
            logger.warning(
                "Quota check failed — memory pressure",
                slot_id=quota.slot_id,
                memory_percent=telemetry.memory_percent,
            )
            return False
        if (
            telemetry.gpu_util_percent is not None
            and telemetry.gpu_util_percent > quota.max_gpu_percent
        ):
            logger.warning(
                "Quota check failed — GPU util exceeds slot cap",
                slot_id=quota.slot_id,
                gpu_util=telemetry.gpu_util_percent,
            )
            return False
        logger.debug("Quota check passed", slot_id=quota.slot_id)
        return True
