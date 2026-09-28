"""Bootstrap inventory index — Edge signal map from Setu configuration."""

from injector import inject

from src.business_services.base_business_service import BaseBusinessService
from src.exceptions import InventoryLookupError, SignalMapError
from src.logging import get_logger
from src.models.signal_map_models import (
    BootstrapConfiguration,
    EndpointRoleType,
    ObserveScheduleEntry,
    ResolvedInventoryEndpoint,
)

logger = get_logger()

InventoryKey = tuple[str, str]


class BootstrapInventoryService(BaseBusinessService):
    """
    Index bootstrap ``configuration.services`` by ``(service_name, endpoint_name)``.

    Observe endpoints are scheduled from inventory only (D5) — stub records
    schedules without running a live scrape loop (W1 mock).
    """

    @inject
    def __init__(self) -> None:
        super().__init__()
        self._index: dict[InventoryKey, ResolvedInventoryEndpoint] = {}
        self._configuration: BootstrapConfiguration | None = None
        self._observe_schedules: list[ObserveScheduleEntry] = []

    @property
    def configuration(self) -> BootstrapConfiguration | None:
        return self._configuration

    @property
    def index(self) -> dict[InventoryKey, ResolvedInventoryEndpoint]:
        return dict(self._index)

    @property
    def observe_schedules(self) -> list[ObserveScheduleEntry]:
        return list(self._observe_schedules)

    def load_configuration(self, configuration: BootstrapConfiguration) -> int:
        """
        Build the inventory index from bootstrap configuration.

        Returns the number of indexed endpoints.
        """
        index: dict[InventoryKey, ResolvedInventoryEndpoint] = {}
        for service in configuration.services:
            for endpoint in service.endpoints:
                key: InventoryKey = (service.service_name, endpoint.endpoint_name)
                if key in index:
                    raise SignalMapError(
                        f"duplicate inventory key: "
                        f"({service.service_name}, {endpoint.endpoint_name})"
                    )
                index[key] = ResolvedInventoryEndpoint(
                    service_name=service.service_name,
                    endpoint_name=endpoint.endpoint_name,
                    base_url=service.base_url,
                    role=endpoint.role,
                    http_method=endpoint.http_method,
                    path=endpoint.path,
                    parameters_schema=endpoint.parameters_schema,
                    interval_seconds=endpoint.interval_seconds,
                )

        self._configuration = configuration
        self._index = index
        self._observe_schedules = []
        logger.info(
            "Bootstrap inventory indexed",
            endpoint_count=len(index),
            service_count=len(configuration.services),
        )
        return len(index)

    def lookup(self, service_name: str, endpoint_name: str) -> ResolvedInventoryEndpoint:
        """Resolve a catalog leaf; fail fast on miss (D1 / REQ-04)."""
        key: InventoryKey = (service_name, endpoint_name)
        resolved = self._index.get(key)
        if resolved is None:
            raise InventoryLookupError(f"inventory miss for ({service_name}, {endpoint_name})")
        return resolved

    def schedule_observe_endpoints(self) -> list[ObserveScheduleEntry]:
        """
        Stub: record observe-role schedules from the index (REQ-02).

        Does not start a timer loop — W1 mock / observe scheduling stub OK.
        Endpoints without ``interval_seconds`` are skipped with a warning.
        """
        schedules: list[ObserveScheduleEntry] = []
        for resolved in self._index.values():
            if resolved.role != EndpointRoleType.OBSERVE:
                continue
            if resolved.interval_seconds is None:
                logger.warning(
                    "Observe endpoint missing interval_seconds — skipped",
                    service_name=resolved.service_name,
                    endpoint_name=resolved.endpoint_name,
                )
                continue
            schedules.append(
                ObserveScheduleEntry(
                    service_name=resolved.service_name,
                    endpoint_name=resolved.endpoint_name,
                    url=resolved.url,
                    http_method=resolved.http_method,
                    interval_seconds=resolved.interval_seconds,
                )
            )

        self._observe_schedules = schedules
        logger.info(
            "Observe scheduling stub recorded",
            schedule_count=len(schedules),
        )
        return list(schedules)
