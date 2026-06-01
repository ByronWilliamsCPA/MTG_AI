"""Core configuration, settings, and exception modules."""

from mtg_ai.core.config import Settings
from mtg_ai.core.exceptions import (
    APIError,
    AuthenticationError,
    AuthorizationError,
    BusinessLogicError,
    ConfigurationError,
    DatabaseError,
    ExternalServiceError,
    ProjectBaseError,
    ResourceNotFoundError,
    ValidationError,
)

__all__ = [
    # Exceptions (sorted alphabetically)
    "APIError",
    "AuthenticationError",
    "AuthorizationError",
    "BusinessLogicError",
    "ConfigurationError",
    "DatabaseError",
    "ExternalServiceError",
    "ProjectBaseError",
    "ResourceNotFoundError",
    # Configuration
    "Settings",
    "ValidationError",
]
