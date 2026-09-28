"""Application exceptions for {{ cookiecutter.agent_name }}."""


class BaseAgentException(Exception):
    """Base exception for agent errors."""

    def __init__(self, message: str, code: str = "AGENT_ERROR") -> None:
        self.message = message
        self.code = code
        super().__init__(message)


class ManifestVerificationError(BaseAgentException):
    """Raised when manifest or artifact verification fails."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="MANIFEST_VERIFICATION_ERROR")


class ReconciliationError(BaseAgentException):
    """Raised when desired-state reconciliation fails."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="RECONCILIATION_ERROR")


class BufferError(BaseAgentException):
    """Raised when buffer operations fail."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="BUFFER_ERROR")


class UnsupportedCommandIdentityError(BaseAgentException):
    """Raised when downlink identity is not autrio.command.v1 (D12)."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="UNSUPPORTED_COMMAND_IDENTITY")


class InventoryLookupError(BaseAgentException):
    """Raised when (service_name, endpoint_name) is missing from bootstrap index."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="INVENTORY_LOOKUP_ERROR")


class SignalMapError(BaseAgentException):
    """Raised when bootstrap inventory or Autrio dispatch fails."""

    def __init__(self, message: str, code: str = "SIGNAL_MAP_ERROR") -> None:
        super().__init__(message, code=code)
