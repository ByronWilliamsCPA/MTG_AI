"""Request correlation middleware for distributed tracing.

This module provides middleware for request ID propagation and correlation,
enabling distributed tracing and log correlation across services.

Features:
- Automatic request ID generation (UUID4)
- Extraction of incoming request IDs from headers
- Context variable storage for async-safe access
- Response header injection
- Structlog integration for log correlation

Standard Headers Supported:
- X-Request-ID: Primary correlation header
- X-Correlation-ID: Alternative correlation header
- X-Trace-ID: Distributed tracing header

Usage:
    from fastapi import FastAPI
    from mtg_ai.middleware.correlation import (
        CorrelationMiddleware,
        get_correlation_id,
    )

    app = FastAPI()
    app.add_middleware(CorrelationMiddleware)

    @app.get("/")
    async def root():
        # Access correlation ID anywhere in request context
        correlation_id = get_correlation_id()
        return {"correlation_id": correlation_id}

Integration with Logging:
    from mtg_ai.middleware.correlation import correlation_context_processor

    # Add to structlog processors
    structlog.configure(
        processors=[
            correlation_context_processor,
            # ... other processors
        ],
    )
"""

from __future__ import annotations

import uuid
from contextvars import ContextVar
from typing import TYPE_CHECKING

from starlette.middleware.base import BaseHTTPMiddleware

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from fastapi import Request
    from starlette.responses import Response
    from structlog.types import EventDict, WrappedLogger

# Context variables for request correlation (async-safe)
_correlation_id_ctx: ContextVar[str | None] = ContextVar("correlation_id", default=None)
_request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)
_trace_id_ctx: ContextVar[str | None] = ContextVar("trace_id", default=None)
_span_id_ctx: ContextVar[str | None] = ContextVar("span_id", default=None)

# Standard header names for correlation
CORRELATION_ID_HEADER = "X-Correlation-ID"
REQUEST_ID_HEADER = "X-Request-ID"
TRACE_ID_HEADER = "X-Trace-ID"
SPAN_ID_HEADER = "X-Span-ID"


def get_correlation_id() -> str | None:
    """Get the current request's correlation ID.

    Returns:
        str | None: Correlation ID string, or None if not in a request context.

    Example:
        >>> from mtg_ai.middleware.correlation import get_correlation_id
        >>> correlation_id = get_correlation_id()
        >>> logger.info("Processing", correlation_id=correlation_id)
    """
    return _correlation_id_ctx.get()


def get_request_id() -> str | None:
    """Get the current request's unique request ID.

    Returns:
        str | None: Request ID string, or None if not in a request context.
    """
    return _request_id_ctx.get()


def get_trace_id() -> str | None:
    """Get the current request's trace ID for distributed tracing.

    Returns:
        str | None: Trace ID string, or None if not in a request context.
    """
    return _trace_id_ctx.get()


def get_span_id() -> str | None:
    """Get the current request's span ID.

    Returns:
        str | None: Span ID string, or None if not in a request context.
    """
    return _span_id_ctx.get()


def set_correlation_id(correlation_id: str) -> None:
    """Set the correlation ID in the current context.

    Useful for background jobs or non-HTTP contexts.

    Args:
        correlation_id: The correlation ID to set.
    """
    _correlation_id_ctx.set(correlation_id)


def generate_correlation_id() -> str:
    """Generate a new correlation ID.

    Returns:
        str: A new UUID4 string suitable for use as a correlation ID.
    """
    return str(uuid.uuid4())


def correlation_context_processor(
    _logger: WrappedLogger,
    _method_name: str,
    event_dict: EventDict,
) -> EventDict:
    """Structlog processor to add correlation context to log entries.

    This processor automatically adds correlation IDs to all log entries
    when running in a request context.

    Add this to your structlog configuration:
        structlog.configure(
            processors=[
                correlation_context_processor,
                # ... other processors
            ],
        )

    Args:
        _logger: The wrapped logger instance.
        _method_name: The name of the log method called.
        event_dict: The event dictionary to process.

    Returns:
        EventDict: Updated event dictionary with correlation IDs.
    """
    correlation_id = _correlation_id_ctx.get()
    request_id = _request_id_ctx.get()
    trace_id = _trace_id_ctx.get()
    span_id = _span_id_ctx.get()

    if correlation_id:
        event_dict["correlation_id"] = correlation_id
    if request_id:
        event_dict["request_id"] = request_id
    if trace_id:
        event_dict["trace_id"] = trace_id
    if span_id:
        event_dict["span_id"] = span_id

    return event_dict


class CorrelationMiddleware(BaseHTTPMiddleware):
    """Middleware for request correlation ID propagation.

    Extracts or generates correlation IDs for each request and stores them
    in context variables for access throughout the request lifecycle.

    Header Priority:
    1. X-Correlation-ID (primary)
    2. X-Request-ID (fallback)
    3. X-Trace-ID (for distributed tracing)
    4. Generate new UUID if none provided

    Features:
    - Extracts existing correlation IDs from incoming requests
    - Generates new IDs for requests without correlation headers
    - Stores IDs in async-safe context variables
    - Adds correlation headers to responses
    - Supports distributed tracing headers (X-Trace-ID, X-Span-ID)

    Example:
        >>> from fastapi import FastAPI
        >>> app = FastAPI()
        >>> app.add_middleware(CorrelationMiddleware)
    """

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Process request with correlation ID handling.

        Args:
            request: The incoming HTTP request.
            call_next: The next middleware or route handler.

        Returns:
            Response: The HTTP response with correlation headers added.
        """
        # Extract or generate correlation ID
        correlation_id = (
            request.headers.get(CORRELATION_ID_HEADER)
            or request.headers.get(REQUEST_ID_HEADER)
            or generate_correlation_id()
        )

        # Generate unique request ID for this specific request
        request_id = request.headers.get(REQUEST_ID_HEADER) or generate_correlation_id()

        # Extract distributed tracing headers
        trace_id = request.headers.get(TRACE_ID_HEADER)
        span_id = request.headers.get(SPAN_ID_HEADER)

        # Set context variables
        correlation_token = _correlation_id_ctx.set(correlation_id)
        request_token = _request_id_ctx.set(request_id)
        trace_token = _trace_id_ctx.set(trace_id) if trace_id else None
        span_token = _span_id_ctx.set(span_id) if span_id else None

        try:
            response = await call_next(request)

            # Add correlation headers to response
            response.headers[CORRELATION_ID_HEADER] = correlation_id
            response.headers[REQUEST_ID_HEADER] = request_id

            # Forward tracing headers if present
            if trace_id:
                response.headers[TRACE_ID_HEADER] = trace_id
            if span_id:
                response.headers[SPAN_ID_HEADER] = span_id

            return response

        finally:
            # Reset context variables
            _correlation_id_ctx.reset(correlation_token)
            _request_id_ctx.reset(request_token)
            if trace_token:
                _trace_id_ctx.reset(trace_token)
            if span_token:
                _span_id_ctx.reset(span_token)


# Export public API
__all__ = [
    "CORRELATION_ID_HEADER",
    "REQUEST_ID_HEADER",
    "SPAN_ID_HEADER",
    "TRACE_ID_HEADER",
    "CorrelationMiddleware",
    "correlation_context_processor",
    "generate_correlation_id",
    "get_correlation_id",
    "get_request_id",
    "get_span_id",
    "get_trace_id",
    "set_correlation_id",
]
