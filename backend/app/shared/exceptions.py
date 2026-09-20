"""
Domain-level exceptions. Services raise these; they know nothing about
HTTP. The global exception handler in app/main.py maps each one to the
appropriate HTTP status code and JSON error shape.
"""


class DomainError(Exception):
    """Base class for all domain/business-rule errors."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class NotFoundError(DomainError):
    """Raised when a requested entity does not exist."""


class OwnershipError(DomainError):
    """Raised when the requesting device does not own the resource (403)."""


class ValidationDomainError(DomainError):
    """Raised for business-rule validation failures that aren't simple
    Pydantic shape issues (e.g. reordering with an invalid place id)."""


class ExternalProviderError(DomainError):
    """Raised when an external provider (Neshan map/place API) fails or
    is unreachable. Handlers turn this into a graceful fallback response,
    never a bare 500."""


class UnauthorizedError(DomainError):
    """Raised when authentication is required or the bearer token is invalid."""
