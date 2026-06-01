"""Tests for security middleware components.

Covers SecurityHeadersMiddleware, RateLimitMiddleware, SSRFPreventionMiddleware,
and the add_security_middleware helper.
"""

from __future__ import annotations

import time
from unittest.mock import MagicMock

import pytest


class TestSecurityHeadersMiddleware:
    """Tests for SecurityHeadersMiddleware OWASP header injection."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_dispatch_adds_content_type_options_header(self) -> None:
        """Verify X-Content-Type-Options: nosniff is added to every response."""
        from mtg_ai.middleware.security import SecurityHeadersMiddleware

        middleware = SecurityHeadersMiddleware(app=MagicMock())
        mock_request = MagicMock()
        mock_request.url.scheme = "http"
        mock_response = MagicMock()
        mock_response.headers = {}

        async def call_next(_req):
            return mock_response

        response = await middleware.dispatch(mock_request, call_next)

        assert response.headers["X-Content-Type-Options"] == "nosniff"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_dispatch_adds_frame_options_header(self) -> None:
        """Verify X-Frame-Options: DENY is added to prevent clickjacking."""
        from mtg_ai.middleware.security import SecurityHeadersMiddleware

        middleware = SecurityHeadersMiddleware(app=MagicMock())
        mock_request = MagicMock()
        mock_request.url.scheme = "http"
        mock_response = MagicMock()
        mock_response.headers = {}

        async def call_next(_req):
            return mock_response

        response = await middleware.dispatch(mock_request, call_next)

        assert response.headers["X-Frame-Options"] == "DENY"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_dispatch_adds_xss_protection_header(self) -> None:
        """Verify X-XSS-Protection header is added."""
        from mtg_ai.middleware.security import SecurityHeadersMiddleware

        middleware = SecurityHeadersMiddleware(app=MagicMock())
        mock_request = MagicMock()
        mock_request.url.scheme = "http"
        mock_response = MagicMock()
        mock_response.headers = {}

        async def call_next(_req):
            return mock_response

        response = await middleware.dispatch(mock_request, call_next)

        assert response.headers["X-XSS-Protection"] == "1; mode=block"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_dispatch_adds_csp_header(self) -> None:
        """Verify Content-Security-Policy header is present."""
        from mtg_ai.middleware.security import SecurityHeadersMiddleware

        middleware = SecurityHeadersMiddleware(app=MagicMock())
        mock_request = MagicMock()
        mock_request.url.scheme = "http"
        mock_response = MagicMock()
        mock_response.headers = {}

        async def call_next(_req):
            return mock_response

        response = await middleware.dispatch(mock_request, call_next)

        assert "default-src" in response.headers["Content-Security-Policy"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_dispatch_adds_referrer_policy_header(self) -> None:
        """Verify Referrer-Policy header is added."""
        from mtg_ai.middleware.security import SecurityHeadersMiddleware

        middleware = SecurityHeadersMiddleware(app=MagicMock())
        mock_request = MagicMock()
        mock_request.url.scheme = "http"
        mock_response = MagicMock()
        mock_response.headers = {}

        async def call_next(_req):
            return mock_response

        response = await middleware.dispatch(mock_request, call_next)

        assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_dispatch_adds_permissions_policy_header(self) -> None:
        """Verify Permissions-Policy header restricts browser features."""
        from mtg_ai.middleware.security import SecurityHeadersMiddleware

        middleware = SecurityHeadersMiddleware(app=MagicMock())
        mock_request = MagicMock()
        mock_request.url.scheme = "http"
        mock_response = MagicMock()
        mock_response.headers = {}

        async def call_next(_req):
            return mock_response

        response = await middleware.dispatch(mock_request, call_next)

        assert "geolocation=()" in response.headers["Permissions-Policy"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_dispatch_adds_hsts_for_https(self) -> None:
        """Verify Strict-Transport-Security is added only for HTTPS requests."""
        from mtg_ai.middleware.security import SecurityHeadersMiddleware

        middleware = SecurityHeadersMiddleware(app=MagicMock())
        mock_request = MagicMock()
        mock_request.url.scheme = "https"
        mock_response = MagicMock()
        mock_response.headers = {}

        async def call_next(_req):
            return mock_response

        response = await middleware.dispatch(mock_request, call_next)

        assert "max-age=31536000" in response.headers["Strict-Transport-Security"]
        assert "includeSubDomains" in response.headers["Strict-Transport-Security"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_dispatch_no_hsts_for_http(self) -> None:
        """Verify Strict-Transport-Security is NOT added for plain HTTP requests."""
        from mtg_ai.middleware.security import SecurityHeadersMiddleware

        middleware = SecurityHeadersMiddleware(app=MagicMock())
        mock_request = MagicMock()
        mock_request.url.scheme = "http"
        mock_response = MagicMock()
        mock_response.headers = {}

        async def call_next(_req):
            return mock_response

        response = await middleware.dispatch(mock_request, call_next)

        assert "Strict-Transport-Security" not in response.headers

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_dispatch_removes_server_header(self) -> None:
        """Verify Server header is stripped to prevent information disclosure."""
        from mtg_ai.middleware.security import SecurityHeadersMiddleware

        middleware = SecurityHeadersMiddleware(app=MagicMock())
        mock_request = MagicMock()
        mock_request.url.scheme = "http"
        mock_response = MagicMock()
        mock_response.headers = {"Server": "uvicorn/0.24.0"}

        async def call_next(_req):
            return mock_response

        await middleware.dispatch(mock_request, call_next)

        assert "Server" not in mock_response.headers


class TestRateLimitMiddleware:
    """Tests for in-memory rate limiting."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_allows_requests_under_rate_limit(self) -> None:
        """Verify requests below the rate limit are passed through."""
        from mtg_ai.middleware.security import RateLimitMiddleware

        middleware = RateLimitMiddleware(app=MagicMock(), requests_per_minute=60)
        mock_request = MagicMock()
        mock_request.client.host = "192.0.2.1"
        expected = MagicMock()

        async def call_next(_req):
            return expected

        response = await middleware.dispatch(mock_request, call_next)

        assert response is expected

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_blocks_requests_over_rate_limit(self) -> None:
        """Verify 429 is returned when requests_per_minute is exceeded."""
        from mtg_ai.middleware.security import RateLimitMiddleware

        middleware = RateLimitMiddleware(app=MagicMock(), requests_per_minute=2)
        ip = "192.0.2.2"
        now = time.time()
        middleware.requests[ip] = [now, now]

        mock_request = MagicMock()
        mock_request.client.host = ip

        async def call_next(_req):
            return MagicMock()

        response = await middleware.dispatch(mock_request, call_next)

        assert response.status_code == 429

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_blocks_burst_requests(self) -> None:
        """Verify 429 is returned when burst_size is exceeded within 1 second."""
        from mtg_ai.middleware.security import RateLimitMiddleware

        middleware = RateLimitMiddleware(
            app=MagicMock(), requests_per_minute=100, burst_size=2
        )
        ip = "192.0.2.3"
        now = time.time()
        middleware.requests[ip] = [now, now]

        mock_request = MagicMock()
        mock_request.client.host = ip

        async def call_next(_req):
            return MagicMock()

        response = await middleware.dispatch(mock_request, call_next)

        assert response.status_code == 429

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_handles_none_client(self) -> None:
        """Verify middleware uses 'unknown' fallback when client IP is unavailable."""
        from mtg_ai.middleware.security import RateLimitMiddleware

        middleware = RateLimitMiddleware(app=MagicMock(), requests_per_minute=60)
        mock_request = MagicMock()
        mock_request.client = None
        expected = MagicMock()

        async def call_next(_req):
            return expected

        response = await middleware.dispatch(mock_request, call_next)

        assert response is expected

    @pytest.mark.unit
    def test_cleanup_removes_stale_entries(self) -> None:
        """Verify _cleanup_stale_entries removes expired timestamps."""
        from mtg_ai.middleware.security import RateLimitMiddleware

        middleware = RateLimitMiddleware(app=MagicMock(), cleanup_interval=0)
        old = time.time() - 120
        middleware.requests["stale"] = [old]
        middleware._last_cleanup = 0

        middleware._cleanup_stale_entries(time.time())

        assert "stale" not in middleware.requests

    @pytest.mark.unit
    def test_cleanup_trims_over_max_tracked_ips(self) -> None:
        """Verify _cleanup_stale_entries enforces max_tracked_ips limit."""
        from mtg_ai.middleware.security import RateLimitMiddleware

        middleware = RateLimitMiddleware(
            app=MagicMock(), cleanup_interval=0, max_tracked_ips=2
        )
        now = time.time()
        for i in range(5):
            middleware.requests[f"10.0.0.{i}"] = [now]
        middleware._last_cleanup = 0

        middleware._cleanup_stale_entries(now)

        assert len(middleware.requests) <= 2

    @pytest.mark.unit
    def test_cleanup_skipped_before_interval(self) -> None:
        """Verify cleanup does not run before cleanup_interval has elapsed."""
        from mtg_ai.middleware.security import RateLimitMiddleware

        middleware = RateLimitMiddleware(app=MagicMock(), cleanup_interval=3600)
        old = time.time() - 120
        middleware.requests["ip"] = [old]
        middleware._last_cleanup = time.time()

        middleware._cleanup_stale_entries(time.time())

        assert "ip" in middleware.requests


class TestSSRFPreventionMiddleware:
    """Tests for SSRF prevention middleware."""

    @pytest.mark.unit
    def test_is_private_ip_loopback(self) -> None:
        """Verify loopback addresses are classified as private."""
        from mtg_ai.middleware.security import SSRFPreventionMiddleware

        assert SSRFPreventionMiddleware._is_private_ip("127.0.0.1") is True
        assert SSRFPreventionMiddleware._is_private_ip("::1") is True

    @pytest.mark.unit
    def test_is_private_ip_rfc1918(self) -> None:
        """Verify RFC-1918 private ranges are classified as private."""
        from mtg_ai.middleware.security import SSRFPreventionMiddleware

        assert SSRFPreventionMiddleware._is_private_ip("10.0.0.1") is True
        assert SSRFPreventionMiddleware._is_private_ip("172.16.0.1") is True
        assert SSRFPreventionMiddleware._is_private_ip("192.168.1.1") is True

    @pytest.mark.unit
    def test_is_private_ip_public(self) -> None:
        """Verify public IPs are not classified as private."""
        from mtg_ai.middleware.security import SSRFPreventionMiddleware

        assert SSRFPreventionMiddleware._is_private_ip("8.8.8.8") is False
        assert SSRFPreventionMiddleware._is_private_ip("1.1.1.1") is False

    @pytest.mark.unit
    def test_is_private_ip_invalid_string(self) -> None:
        """Verify invalid IP strings return False without raising."""
        from mtg_ai.middleware.security import SSRFPreventionMiddleware

        assert SSRFPreventionMiddleware._is_private_ip("not-an-ip") is False

    @pytest.mark.unit
    def test_is_private_ip_ipv4_mapped_ipv6(self) -> None:
        """Verify IPv4-mapped IPv6 loopback is classified as private."""
        from mtg_ai.middleware.security import SSRFPreventionMiddleware

        assert SSRFPreventionMiddleware._is_private_ip("::ffff:127.0.0.1") is True

    @pytest.mark.unit
    def test_extract_host_from_url_valid(self) -> None:
        """Verify hostname is correctly extracted from a URL."""
        from mtg_ai.middleware.security import SSRFPreventionMiddleware

        result = SSRFPreventionMiddleware._extract_host_from_url(
            "http://example.com/path"
        )
        assert result == "example.com"

    @pytest.mark.unit
    def test_extract_host_from_url_relative(self) -> None:
        """Verify relative paths return None for hostname."""
        from mtg_ai.middleware.security import SSRFPreventionMiddleware

        result = SSRFPreventionMiddleware._extract_host_from_url("/relative/path")
        assert result is None

    @pytest.mark.unit
    def test_extract_scheme_from_url_http(self) -> None:
        """Verify scheme is extracted correctly."""
        from mtg_ai.middleware.security import SSRFPreventionMiddleware

        assert (
            SSRFPreventionMiddleware._extract_scheme_from_url("http://example.com")
            == "http"
        )
        assert (
            SSRFPreventionMiddleware._extract_scheme_from_url("ftp://files.example.com")
            == "ftp"
        )

    @pytest.mark.unit
    def test_extract_scheme_from_url_empty(self) -> None:
        """Verify None is returned when no scheme is present."""
        from mtg_ai.middleware.security import SSRFPreventionMiddleware

        result = SSRFPreventionMiddleware._extract_scheme_from_url("/no-scheme")
        assert result is None

    @pytest.mark.unit
    def test_is_blocked_url_private_ip(self) -> None:
        """Verify URLs pointing to private IP ranges are blocked."""
        from mtg_ai.middleware.security import SSRFPreventionMiddleware

        m = SSRFPreventionMiddleware(app=MagicMock())

        assert m._is_blocked_url("http://127.0.0.1/admin") is True
        assert m._is_blocked_url("http://192.168.0.1/secret") is True
        assert m._is_blocked_url("http://10.0.0.1/internal") is True

    @pytest.mark.unit
    def test_is_blocked_url_blocked_hostname(self) -> None:
        """Verify explicitly blocked hostnames are rejected."""
        from mtg_ai.middleware.security import SSRFPreventionMiddleware

        m = SSRFPreventionMiddleware(app=MagicMock())

        assert m._is_blocked_url("http://localhost/secret") is True
        assert m._is_blocked_url("http://metadata.google.internal/") is True

    @pytest.mark.unit
    def test_is_blocked_url_blocked_scheme(self) -> None:
        """Verify dangerous URL schemes are blocked."""
        from mtg_ai.middleware.security import SSRFPreventionMiddleware

        m = SSRFPreventionMiddleware(app=MagicMock())

        assert m._is_blocked_url("file:///etc/passwd") is True
        assert m._is_blocked_url("gopher://evil.com") is True
        assert m._is_blocked_url("dict://evil.com") is True

    @pytest.mark.unit
    def test_is_blocked_url_decimal_ip_obfuscation(self) -> None:
        """Verify decimal-encoded IP (e.g. 2130706433 = 127.0.0.1) is blocked."""
        from mtg_ai.middleware.security import SSRFPreventionMiddleware

        m = SSRFPreventionMiddleware(app=MagicMock())

        assert m._is_blocked_url("http://2130706433/secret") is True

    @pytest.mark.unit
    def test_is_blocked_url_public(self) -> None:
        """Verify URLs with legitimate public hostnames are not blocked."""
        from mtg_ai.middleware.security import SSRFPreventionMiddleware

        m = SSRFPreventionMiddleware(app=MagicMock())

        assert m._is_blocked_url("https://api.example.com/data") is False

    @pytest.mark.unit
    def test_is_blocked_url_no_host(self) -> None:
        """Verify URLs with no host component are not blocked."""
        from mtg_ai.middleware.security import SSRFPreventionMiddleware

        m = SSRFPreventionMiddleware(app=MagicMock())

        assert m._is_blocked_url("/relative/path") is False

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_dispatch_blocks_ssrf_url_in_query_param(self) -> None:
        """Verify 400 is returned when a query param contains a blocked URL."""
        from mtg_ai.middleware.security import SSRFPreventionMiddleware

        m = SSRFPreventionMiddleware(app=MagicMock())
        mock_request = MagicMock()
        mock_request.query_params = {"url": "http://127.0.0.1/admin"}

        async def call_next(_req):
            return MagicMock()

        response = await m.dispatch(mock_request, call_next)

        assert response.status_code == 400

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_dispatch_allows_safe_query_params(self) -> None:
        """Verify requests with safe query params pass through."""
        from mtg_ai.middleware.security import SSRFPreventionMiddleware

        m = SSRFPreventionMiddleware(app=MagicMock())
        mock_request = MagicMock()
        mock_request.query_params = {"url": "https://api.example.com/v1/data"}
        expected = MagicMock()

        async def call_next(_req):
            return expected

        response = await m.dispatch(mock_request, call_next)

        assert response is expected

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_dispatch_allows_non_url_params(self) -> None:
        """Verify requests with no URL-like params pass through unchanged."""
        from mtg_ai.middleware.security import SSRFPreventionMiddleware

        m = SSRFPreventionMiddleware(app=MagicMock())
        mock_request = MagicMock()
        mock_request.query_params = {"page": "1", "limit": "25", "sort": "asc"}
        expected = MagicMock()

        async def call_next(_req):
            return expected

        response = await m.dispatch(mock_request, call_next)

        assert response is expected


class TestAddSecurityMiddleware:
    """Tests for the add_security_middleware factory function."""

    @pytest.mark.unit
    def test_adds_middleware_with_defaults(self) -> None:
        """Verify at least one middleware is added with default settings."""
        from fastapi import FastAPI

        from mtg_ai.middleware.security import add_security_middleware

        app = FastAPI()
        add_security_middleware(app)

        assert len(app.user_middleware) > 0

    @pytest.mark.unit
    def test_adds_https_redirect_when_enabled(self) -> None:
        """Verify HTTPSRedirectMiddleware is added when enable_https_redirect=True."""
        from fastapi import FastAPI
        from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware

        from mtg_ai.middleware.security import add_security_middleware

        app = FastAPI()
        add_security_middleware(app, enable_https_redirect=True)

        middleware_classes = [m.cls for m in app.user_middleware]
        assert HTTPSRedirectMiddleware in middleware_classes

    @pytest.mark.unit
    def test_adds_trusted_host_when_allowed_hosts_provided(self) -> None:
        """Verify TrustedHostMiddleware is added when allowed_hosts is set."""
        from fastapi import FastAPI
        from starlette.middleware.trustedhost import TrustedHostMiddleware

        from mtg_ai.middleware.security import add_security_middleware

        app = FastAPI()
        add_security_middleware(app, allowed_hosts=["api.example.com"])

        middleware_classes = [m.cls for m in app.user_middleware]
        assert TrustedHostMiddleware in middleware_classes

    @pytest.mark.unit
    def test_omits_rate_limiter_when_disabled(self) -> None:
        """Verify RateLimitMiddleware is absent when enable_rate_limiting=False."""
        from fastapi import FastAPI

        from mtg_ai.middleware.security import (
            RateLimitMiddleware,
            add_security_middleware,
        )

        app = FastAPI()
        add_security_middleware(app, enable_rate_limiting=False)

        middleware_classes = [m.cls for m in app.user_middleware]
        assert RateLimitMiddleware not in middleware_classes

    @pytest.mark.unit
    def test_omits_ssrf_prevention_when_disabled(self) -> None:
        """Verify SSRFPreventionMiddleware is absent when enable_ssrf_prevention=False."""
        from fastapi import FastAPI

        from mtg_ai.middleware.security import (
            SSRFPreventionMiddleware,
            add_security_middleware,
        )

        app = FastAPI()
        add_security_middleware(app, enable_ssrf_prevention=False)

        middleware_classes = [m.cls for m in app.user_middleware]
        assert SSRFPreventionMiddleware not in middleware_classes
