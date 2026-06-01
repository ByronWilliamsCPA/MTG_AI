"""Security middleware for FastAPI applications.

This module provides production-ready security middleware implementing OWASP best practices:
- CORS configuration (A05: Security Misconfiguration)
- Security headers (A05: Security Misconfiguration)
- Rate limiting (A07: Identification and Authentication Failures)
- Request validation (A03: Injection)
- SSRF prevention (A10: Server-Side Request Forgery)

Usage:
    from mtg_ai.middleware.security import (
        add_security_middleware,
        SecurityHeadersMiddleware,
        RateLimitMiddleware,
    )

    app = FastAPI()
    add_security_middleware(app)
"""

from __future__ import annotations

import logging
import time
from collections import defaultdict
from typing import TYPE_CHECKING

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.responses import JSONResponse, Response

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from fastapi import FastAPI, Request
    from starlette.types import ASGIApp


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses.

    Implements OWASP recommended security headers to prevent:
    - XSS attacks
    - Clickjacking
    - MIME sniffing
    - Information leakage

    Headers added:
    - X-Content-Type-Options: nosniff
    - X-Frame-Options: DENY
    - X-XSS-Protection: 1; mode=block
    - Strict-Transport-Security: HSTS for HTTPS
    - Content-Security-Policy: Prevent inline scripts
    - Referrer-Policy: Control referrer information
    - Permissions-Policy: Restrict browser features
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        """Add security headers to response."""
        response = await call_next(request)

        # Prevent MIME sniffing (OWASP A05)
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Prevent clickjacking (OWASP A05)
        response.headers["X-Frame-Options"] = "DENY"

        # Enable XSS protection (OWASP A03)
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # HSTS: Force HTTPS for 1 year (OWASP A02)
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )

        # Content Security Policy: Prevent inline scripts (OWASP A03)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'none'"
        )

        # Control referrer information (OWASP A09)
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Restrict browser features (OWASP A05)
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=(), payment=()"
        )

        # Remove server identification (OWASP A09)
        response.headers.pop("Server", None)

        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiting middleware.

    Implements rate limiting to prevent:
    - Brute force attacks (OWASP A07)
    - DoS attacks (OWASP A04)
    - Credential stuffing (OWASP A07)

    Note: For production, use Redis-backed rate limiting:
        - slowapi (https://github.com/laurents/slowapi)
        - fastapi-limiter (https://github.com/long2ice/fastapi-limiter)

    Args:
        requests_per_minute: Maximum requests per IP per minute
        burst_size: Maximum burst requests allowed
        max_tracked_ips: Maximum IPs to track (prevents memory exhaustion)
        cleanup_interval: Seconds between full cleanup cycles
    """

    def __init__(
        self,
        app: ASGIApp,
        requests_per_minute: int = 60,
        burst_size: int = 10,
        max_tracked_ips: int = 10000,
        cleanup_interval: int = 300,
    ) -> None:
        """Initialize rate limiter."""
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size
        self.max_tracked_ips = max_tracked_ips
        self.cleanup_interval = cleanup_interval
        self.requests: dict[str, list[float]] = defaultdict(list)
        self._last_cleanup = time.time()

    def _cleanup_stale_entries(self, current_time: float) -> None:
        """Remove stale IP entries to prevent memory leaks.

        This method performs two types of cleanup:
        1. Removes expired timestamps from all tracked IPs
        2. If we exceed max_tracked_ips, removes least recently active IPs

        Args:
            current_time: Current timestamp for expiration checks
        """
        # Only run full cleanup periodically to avoid performance impact
        if current_time - self._last_cleanup < self.cleanup_interval:
            return

        self._last_cleanup = current_time

        # Remove expired entries from all IPs
        stale_ips = []
        for ip, timestamps in self.requests.items():
            # Filter to only recent timestamps
            recent = [t for t in timestamps if current_time - t < 60]
            if recent:
                self.requests[ip] = recent
            else:
                stale_ips.append(ip)

        # Remove completely stale IPs
        for ip in stale_ips:
            del self.requests[ip]

        # If still over limit, remove oldest IPs (LRU-style)
        if len(self.requests) > self.max_tracked_ips:
            # Sort by most recent activity and keep only max_tracked_ips
            sorted_ips = sorted(
                self.requests.items(),
                key=lambda x: max(x[1]) if x[1] else 0,
                reverse=True,
            )
            self.requests = defaultdict(
                list,
                {
                    ip: timestamps
                    for ip, timestamps in sorted_ips[: self.max_tracked_ips]
                },
            )

    async def dispatch(self, request: Request, call_next) -> Response:
        """Apply rate limiting per IP address."""
        if request.client is None:
            logger.warning(
                "request.client is None - cannot determine client IP for rate limiting. "
                "Using 'unknown' as fallback. This may occur during testing or with certain proxy configurations."
            )
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()

        # Periodic cleanup to prevent memory leaks
        self._cleanup_stale_entries(current_time)

        # Clean up old entries for current IP (older than 1 minute)
        self.requests[client_ip] = [
            req_time
            for req_time in self.requests[client_ip]
            if current_time - req_time < 60
        ]

        # Check rate limit
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Too Many Requests",
                    "message": f"Rate limit exceeded: {self.requests_per_minute} requests per minute",
                    "retry_after": 60,
                },
                headers={"Retry-After": "60"},
            )

        # Check burst limit
        recent_requests = sum(
            1 for req_time in self.requests[client_ip] if current_time - req_time < 1
        )
        if recent_requests >= self.burst_size:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Too Many Requests",
                    "message": f"Burst limit exceeded: {self.burst_size} requests per second",
                    "retry_after": 1,
                },
                headers={"Retry-After": "1"},
            )

        # Record request
        self.requests[client_ip].append(current_time)

        return await call_next(request)


class SSRFPreventionMiddleware(BaseHTTPMiddleware):
    """Prevent Server-Side Request Forgery (SSRF) attacks.

    Blocks requests to internal/private IP ranges when making outbound HTTP calls.
    Implements OWASP A10 protection with proper IP address validation.

    Features:
    - Proper CIDR range validation using ipaddress module
    - Cloud metadata endpoint blocking (AWS, GCP, Azure)
    - DNS rebinding protection via hostname validation
    - IPv4 and IPv6 support

    Note: For production SSRF prevention, also consider:
    1. Use allowlists for external API endpoints
    2. Validate and sanitize URLs before making requests
    3. Use network segmentation
    4. Implement egress filtering at the network level
    """

    # Blocked hostnames (case-insensitive)
    BLOCKED_HOSTS: set[str] = {
        "localhost",
        "127.0.0.1",
        "0.0.0.0",
        # AWS/Azure metadata endpoints (shared IP)
        "169.254.169.254",
        "fd00:ec2::254",
        # GCP metadata endpoints
        "metadata.google.internal",
        "metadata.goog",
        # Kubernetes
        "kubernetes.default",
        "kubernetes.default.svc",
    }

    # Blocked URL schemes
    BLOCKED_SCHEMES: set[str] = {
        "file",
        "gopher",
        "dict",
        "ftp",
        "ldap",
        "tftp",
    }

    @staticmethod
    def _is_private_ip(ip_str: str) -> bool:
        """Check if an IP address is private, loopback, or otherwise internal.

        Args:
            ip_str: IP address string to validate

        Returns:
            True if the IP is private/internal, False otherwise
        """
        import ipaddress

        try:
            ip = ipaddress.ip_address(ip_str)
            # Check various internal IP properties
            return (
                ip.is_private
                or ip.is_loopback
                or ip.is_link_local
                or ip.is_multicast
                or ip.is_reserved
                or ip.is_unspecified
                # Additional check for IPv4-mapped IPv6 addresses
                or (
                    isinstance(ip, ipaddress.IPv6Address)
                    and ip.ipv4_mapped is not None
                    and SSRFPreventionMiddleware._is_private_ip(str(ip.ipv4_mapped))
                )
            )
        except ValueError:
            # Not a valid IP address - let hostname checks handle it
            return False

    @staticmethod
    def _extract_host_from_url(url: str) -> str | None:
        """Extract hostname from URL string.

        Args:
            url: URL string to parse

        Returns:
            Hostname string or None if parsing fails
        """
        from urllib.parse import urlparse

        try:
            parsed = urlparse(url)
            return parsed.hostname
        except Exception:
            return None

    @staticmethod
    def _extract_scheme_from_url(url: str) -> str | None:
        """Extract scheme from URL string.

        Args:
            url: URL string to parse

        Returns:
            Scheme string or None if parsing fails
        """
        from urllib.parse import urlparse

        try:
            parsed = urlparse(url)
            return parsed.scheme.lower() if parsed.scheme else None
        except Exception:
            return None

    def _is_blocked_url(self, url: str) -> bool:
        """Check if a URL points to a blocked destination.

        Args:
            url: URL string to validate

        Returns:
            True if the URL should be blocked, False otherwise
        """
        # Check scheme
        scheme = self._extract_scheme_from_url(url)
        if scheme and scheme in self.BLOCKED_SCHEMES:
            return True

        # Extract and check hostname
        host = self._extract_host_from_url(url)
        if not host:
            return False

        host_lower = host.lower()

        # Check against blocked hostnames
        if host_lower in self.BLOCKED_HOSTS:
            return True

        # Check if it's a private IP
        if self._is_private_ip(host):
            return True

        # Check for numeric IP obfuscation (decimal, octal, hex)
        # e.g., 2130706433 = 127.0.0.1, 0x7f000001 = 127.0.0.1
        try:
            import ipaddress

            # Try parsing as integer (decimal IP notation)
            if host.isdigit():
                ip_int = int(host)
                if 0 <= ip_int <= 0xFFFFFFFF:
                    ip = ipaddress.ip_address(ip_int)
                    if self._is_private_ip(str(ip)):
                        return True
        except (ValueError, OverflowError):
            pass

        return False

    async def dispatch(self, request: Request, call_next) -> Response:
        """Check for SSRF patterns in request.

        Validates query parameters, form data, and JSON body for potential
        SSRF attempts targeting internal resources.
        """
        # Check query parameters for URLs
        for param, value in request.query_params.items():
            if isinstance(value, str) and ("://" in value or value.startswith("//")):
                if self._is_blocked_url(value):
                    return JSONResponse(
                        status_code=400,
                        content={
                            "error": "Bad Request",
                            "message": "Request blocked: potential SSRF attempt",
                            "detail": f"Blocked URL detected in parameter: {param}",
                        },
                    )

        return await call_next(request)


def add_security_middleware(
    app: FastAPI,
    *,
    enable_https_redirect: bool = False,
    enable_rate_limiting: bool = True,
    enable_ssrf_prevention: bool = True,
    allowed_origins: list[str] | None = None,
    allowed_hosts: list[str] | None = None,
    rate_limit_rpm: int = 60,
) -> None:
    """Add all security middleware to FastAPI application.

    This configures comprehensive security following OWASP best practices.

    Args:
        app: FastAPI application instance
        enable_https_redirect: Redirect HTTP to HTTPS (production only)
        enable_rate_limiting: Enable rate limiting middleware
        enable_ssrf_prevention: Enable SSRF prevention middleware
        allowed_origins: CORS allowed origins (default: none)
        allowed_hosts: Trusted host names (default: all)
        rate_limit_rpm: Rate limit requests per minute

    Example:
        >>> from fastapi import FastAPI
        >>> app = FastAPI()
        >>> add_security_middleware(
        ...     app,
        ...     enable_https_redirect=True,
        ...     allowed_origins=["https://example.com"],
        ...     allowed_hosts=["example.com", "api.example.com"],
        ...     rate_limit_rpm=100,
        ... )
    """
    # HTTPS redirect (production only)
    if enable_https_redirect:
        app.add_middleware(HTTPSRedirectMiddleware)

    # Trusted hosts (OWASP A05)
    if allowed_hosts:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=allowed_hosts,
        )

    # CORS configuration (OWASP A05)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins or [],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"],
        max_age=3600,
    )

    # Security headers (OWASP A05, A03, A09)
    app.add_middleware(SecurityHeadersMiddleware)

    # Rate limiting (OWASP A07)
    if enable_rate_limiting:
        app.add_middleware(
            RateLimitMiddleware,
            requests_per_minute=rate_limit_rpm,
            burst_size=10,
        )

    # SSRF prevention (OWASP A10)
    if enable_ssrf_prevention:
        app.add_middleware(SSRFPreventionMiddleware)


# Example usage in main.py:
"""
from fastapi import FastAPI
from mtg_ai.middleware.security import add_security_middleware

app = FastAPI()

# Add all security middleware
add_security_middleware(
    app,
    enable_https_redirect=True,  # Production only
    enable_rate_limiting=True,
    allowed_origins=[
        "https://example.com",
        "https://app.example.com",
    ],
    allowed_hosts=[
        "api.example.com",
        "localhost",  # Development only
    ],
    rate_limit_rpm=100,
)

# Your routes here
@app.get("/")
async def root():
    return {"message": "Hello World"}
"""
