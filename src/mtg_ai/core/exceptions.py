"""Centralized exception hierarchy for MTG AI.

This module provides a structured exception hierarchy for consistent error handling
across the application. All project-specific exceptions inherit from ProjectBaseError.

Exception Hierarchy:
    ProjectBaseError (base for all project exceptions)
    ├── ConfigurationError (configuration/settings issues)
    ├── ValidationError (input/data validation failures)
    ├── ResourceNotFoundError (missing resources/entities)
    ├── AuthenticationError (authentication failures)
    ├── AuthorizationError (permission/access denied)
    ├── ExternalServiceError (third-party service failures)
    │   ├── APIError (external API errors)
    │   └── DatabaseError (database operation errors)
    └── BusinessLogicError (domain/business rule violations)

Usage:
    from mtg_ai.core.exceptions import (
        ValidationError,
        ResourceNotFoundError,
        ConfigurationError,
    )

    # Raise with context
    raise ValidationError("Invalid email format", field="email", value=user_input)

    # Handle in API endpoints
    try:
        process_data(input_data)
    except ValidationError as e:
        return {"error": str(e), "details": e.details}
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


def _attach_optional_details(
    details: dict[str, Any],
    **fields: Any,
) -> dict[str, Any]:
    """Add non-None field values to a details dict.

    Used by exception ``__init__`` methods to consolidate the repeated
    ``if X: details[X] = X`` pattern. None-valued fields are skipped;
    falsy-but-not-None values (e.g., empty strings, 0, []) are kept
    because the original ``if X:`` pattern would have dropped them but
    callers may want to surface them in the structured details.

    Args:
        details: Existing details dict (may be empty, will be mutated).
        **fields: Optional fields to add; None values are skipped.

    Returns:
        The details dict with non-None fields added (modified in place
        and returned for convenience).
    """
    details.update({k: v for k, v in fields.items() if v is not None})
    return details


@dataclass(frozen=True)
class APIErrorContext:
    """Grouped parameters for APIError construction.

    Use this when constructing an APIError needs to pass multiple
    context fields. Equivalent to passing the same fields as keyword
    arguments; either form is accepted by APIError.__init__.

    Example:
        >>> ctx = APIErrorContext(
        ...     service_name="GitHub",
        ...     status_code=429,
        ...     retry_after=60,
        ... )
        >>> raise APIError("Rate limited", context=ctx)
    """

    service_name: str | None = None
    status_code: int | None = None
    retry_after: int | None = None


class ProjectBaseError(Exception):
    """Base exception for all MTG AI errors.

    All custom exceptions in the project should inherit from this class
    to enable unified error handling and logging.

    Attributes:
        message: Human-readable error message.
        details: Additional context about the error (optional).
        error_code: Machine-readable error code for API responses (optional).

    Example:
        >>> raise ProjectBaseError("Something went wrong", error_code="ERR001")
    """

    def __init__(
        self,
        message: str,
        *,
        details: dict[str, Any] | None = None,
        error_code: str | None = None,
    ) -> None:
        """Initialize the exception.

        Args:
            message: Human-readable error description.
            details: Additional context as key-value pairs.
            error_code: Machine-readable error code.
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.error_code = error_code

    def to_dict(self) -> dict[str, Any]:
        """Convert exception to dictionary for API responses.

        Returns:
            Dictionary with error details suitable for JSON serialization.
        """
        result: dict[str, Any] = {
            "error": self.__class__.__name__,
            "message": self.message,
        }
        if self.error_code:
            result["code"] = self.error_code
        if self.details:
            result["details"] = self.details
        return result


class ConfigurationError(ProjectBaseError):
    """Configuration-related errors.

    Raised when there are issues with application configuration,
    environment variables, or settings validation.

    Example:
        >>> raise ConfigurationError(
        ...     "Missing required configuration",
        ...     details={"missing_keys": ["DATABASE_URL", "SECRET_KEY"]},
        ... )
    """


class ValidationError(ProjectBaseError):
    """Input validation errors.

    Raised when user input or data fails validation rules.
    Includes field-level error details for form validation.

    Example:
        >>> raise ValidationError(
        ...     "Invalid email format",
        ...     field="email",
        ...     value="not-an-email",
        ... )
    """

    def __init__(
        self,
        message: str,
        *,
        field: str | None = None,
        value: Any = None,
        details: dict[str, Any] | None = None,
        error_code: str | None = None,
    ) -> None:
        """Initialize validation error with field context.

        Args:
            message: Description of the validation failure.
            field: Name of the field that failed validation.
            value: The invalid value (will be sanitized in logs).
            details: Additional validation context.
            error_code: Machine-readable error code.
        """
        details = _attach_optional_details(details or {}, field=field)
        if value is not None:
            # Truncate long values to avoid log bloat
            str_value = str(value)
            details["value"] = (
                str_value[:100] + "..." if len(str_value) > 100 else str_value
            )
        super().__init__(
            message, details=details, error_code=error_code or "VALIDATION_ERROR"
        )


class ResourceNotFoundError(ProjectBaseError):
    """Resource not found errors.

    Raised when a requested resource (entity, file, record) cannot be found.

    Example:
        >>> raise ResourceNotFoundError(
        ...     "User not found",
        ...     resource_type="User",
        ...     resource_id="user_123",
        ... )
    """

    def __init__(
        self,
        message: str,
        *,
        resource_type: str | None = None,
        resource_id: str | None = None,
        details: dict[str, Any] | None = None,
        error_code: str | None = None,
    ) -> None:
        """Initialize resource not found error.

        Args:
            message: Description of what was not found.
            resource_type: Type of resource (e.g., "User", "Document").
            resource_id: Identifier of the missing resource.
            details: Additional context.
            error_code: Machine-readable error code.
        """
        details = _attach_optional_details(
            details or {},
            resource_type=resource_type,
            resource_id=resource_id,
        )
        super().__init__(message, details=details, error_code=error_code or "NOT_FOUND")


class AuthenticationError(ProjectBaseError):
    """Authentication failures.

    Raised when authentication fails (invalid credentials, expired tokens, etc.).

    Example:
        >>> raise AuthenticationError("Invalid or expired token")
    """

    def __init__(
        self,
        message: str = "Authentication failed",
        *,
        details: dict[str, Any] | None = None,
        error_code: str | None = None,
    ) -> None:
        """Initialize authentication error.

        Args:
            message: Description of authentication failure.
            details: Additional context (avoid including sensitive data).
            error_code: Machine-readable error code.
        """
        super().__init__(
            message, details=details, error_code=error_code or "AUTH_FAILED"
        )


class AuthorizationError(ProjectBaseError):
    """Authorization/permission errors.

    Raised when a user lacks permission to perform an action.

    Example:
        >>> raise AuthorizationError(
        ...     "Insufficient permissions",
        ...     required_permission="admin:write",
        ...     resource="settings",
        ... )
    """

    def __init__(
        self,
        message: str = "Permission denied",
        *,
        required_permission: str | None = None,
        resource: str | None = None,
        details: dict[str, Any] | None = None,
        error_code: str | None = None,
    ) -> None:
        """Initialize authorization error.

        Args:
            message: Description of permission failure.
            required_permission: The permission that was required.
            resource: The resource access was denied to.
            details: Additional context.
            error_code: Machine-readable error code.
        """
        details = _attach_optional_details(
            details or {},
            required_permission=required_permission,
            resource=resource,
        )
        super().__init__(message, details=details, error_code=error_code or "FORBIDDEN")


class ExternalServiceError(ProjectBaseError):
    """External service/dependency errors.

    Base class for errors from external services (APIs, databases, etc.).

    Example:
        >>> raise ExternalServiceError(
        ...     "Payment gateway unavailable",
        ...     service_name="Stripe",
        ...     status_code=503,
        ... )
    """

    def __init__(
        self,
        message: str,
        *,
        service_name: str | None = None,
        status_code: int | None = None,
        details: dict[str, Any] | None = None,
        error_code: str | None = None,
    ) -> None:
        """Initialize external service error.

        Args:
            message: Description of the service error.
            service_name: Name of the external service.
            status_code: HTTP status code if applicable.
            details: Additional context.
            error_code: Machine-readable error code.
        """
        details = _attach_optional_details(
            details or {},
            service_name=service_name,
            status_code=status_code,
        )
        super().__init__(
            message, details=details, error_code=error_code or "EXTERNAL_SERVICE_ERROR"
        )


class APIError(ExternalServiceError):
    """External API errors.

    Raised when calls to external APIs fail.

    Example:
        >>> raise APIError(
        ...     "GitHub API rate limit exceeded",
        ...     service_name="GitHub",
        ...     status_code=429,
        ...     retry_after=60,
        ... )
    """

    def __init__(
        self,
        message: str,
        *,
        service_name: str | None = None,
        status_code: int | None = None,
        retry_after: int | None = None,
        context: APIErrorContext | None = None,
        details: dict[str, Any] | None = None,
        error_code: str | None = None,
    ) -> None:
        """Initialize API error.

        Two equivalent call styles are supported. Pass an APIErrorContext
        for grouped construction, or pass the individual keyword arguments
        directly. If both are provided, fields from ``context`` take
        precedence over the individual keyword arguments.

        Args:
            message: Description of the API error.
            service_name: Name of the external API.
            status_code: HTTP status code from the API.
            retry_after: Seconds to wait before retrying (for rate limits).
            context: Optional grouped fields; overrides individual kwargs
                when provided.
            details: Additional context.
            error_code: Machine-readable error code.
        """
        if context is not None:
            service_name = (
                context.service_name
                if context.service_name is not None
                else service_name
            )
            status_code = (
                context.status_code if context.status_code is not None else status_code
            )
            retry_after = (
                context.retry_after if context.retry_after is not None else retry_after
            )
        details = _attach_optional_details(details or {}, retry_after=retry_after)
        super().__init__(
            message,
            service_name=service_name,
            status_code=status_code,
            details=details,
            error_code=error_code or "API_ERROR",
        )


class DatabaseError(ExternalServiceError):
    """Database operation errors.

    Raised when database operations fail (connection issues, constraint violations, etc.).

    Example:
        >>> raise DatabaseError(
        ...     "Unique constraint violation",
        ...     operation="insert",
        ...     table="users",
        ... )
    """

    def __init__(
        self,
        message: str,
        *,
        operation: str | None = None,
        table: str | None = None,
        details: dict[str, Any] | None = None,
        error_code: str | None = None,
    ) -> None:
        """Initialize database error.

        Args:
            message: Description of the database error.
            operation: The database operation that failed.
            table: The table/collection involved.
            details: Additional context.
            error_code: Machine-readable error code.
        """
        details = _attach_optional_details(
            details or {},
            operation=operation,
            table=table,
        )
        super().__init__(
            message,
            service_name="database",
            details=details,
            error_code=error_code or "DATABASE_ERROR",
        )


class BusinessLogicError(ProjectBaseError):
    """Business logic/domain rule violations.

    Raised when operations violate business rules or domain constraints.

    Example:
        >>> raise BusinessLogicError(
        ...     "Insufficient funds for transfer",
        ...     rule="minimum_balance",
        ...     context={"available": 100, "requested": 150},
        ... )
    """

    def __init__(
        self,
        message: str,
        *,
        rule: str | None = None,
        context: dict[str, Any] | None = None,
        details: dict[str, Any] | None = None,
        error_code: str | None = None,
    ) -> None:
        """Initialize business logic error.

        Args:
            message: Description of the rule violation.
            rule: Name of the business rule violated.
            context: Business context for the violation.
            details: Additional context.
            error_code: Machine-readable error code.
        """
        details = _attach_optional_details(
            details or {},
            rule=rule,
            context=context,
        )
        super().__init__(
            message, details=details, error_code=error_code or "BUSINESS_RULE_VIOLATION"
        )


# Export all exceptions and public helpers
__all__ = [
    "APIError",
    "APIErrorContext",
    "AuthenticationError",
    "AuthorizationError",
    "BusinessLogicError",
    "ConfigurationError",
    "DatabaseError",
    "ExternalServiceError",
    "ProjectBaseError",
    "ResourceNotFoundError",
    "ValidationError",
]
