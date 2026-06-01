"""Security middleware for API applications.

This package provides production-ready security middleware implementing
OWASP best practices for web applications.
"""

from __future__ import annotations

from mtg_ai.middleware.correlation import (
    CORRELATION_ID_HEADER,
    REQUEST_ID_HEADER,
    SPAN_ID_HEADER,
    TRACE_ID_HEADER,
    CorrelationMiddleware,
    correlation_context_processor,
    generate_correlation_id,
    get_correlation_id,
    get_request_id,
    get_span_id,
    get_trace_id,
    set_correlation_id,
)
from mtg_ai.middleware.security import (
    RateLimitMiddleware,
    SecurityHeadersMiddleware,
    SSRFPreventionMiddleware,
    add_security_middleware,
)

__all__ = [
    "CORRELATION_ID_HEADER",
    "REQUEST_ID_HEADER",
    "SPAN_ID_HEADER",
    "TRACE_ID_HEADER",
    "CorrelationMiddleware",
    "RateLimitMiddleware",
    "SSRFPreventionMiddleware",
    "SecurityHeadersMiddleware",
    "add_security_middleware",
    "correlation_context_processor",
    "generate_correlation_id",
    "get_correlation_id",
    "get_request_id",
    "get_span_id",
    "get_trace_id",
    "set_correlation_id",
]
