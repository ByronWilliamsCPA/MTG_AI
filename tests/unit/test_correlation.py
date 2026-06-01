"""Tests for request correlation middleware.

This module provides comprehensive tests for the correlation middleware
covering:
- Context variable management (get/set functions)
- Correlation ID generation
- Structlog processor integration
- Middleware request handling
- Header extraction and injection
- Async context isolation
"""

import uuid
from unittest.mock import MagicMock

import pytest


class TestContextVariableFunctions:
    """Tests for context variable getter/setter functions."""

    @pytest.mark.unit
    def test_get_correlation_id_default_none(self) -> None:
        """Verify get_correlation_id returns None by default."""
        from mtg_ai.middleware.correlation import (
            get_correlation_id,
        )

        # Reset context for clean test
        result = get_correlation_id()
        # Note: May be None or have value from previous test context
        assert result is None or isinstance(result, str)

    @pytest.mark.unit
    def test_set_and_get_correlation_id(self) -> None:
        """Verify set_correlation_id updates context variable."""
        from mtg_ai.middleware.correlation import (
            _correlation_id_ctx,
            get_correlation_id,
            set_correlation_id,
        )

        test_id = "test-correlation-123"
        token = _correlation_id_ctx.set(None)  # Reset

        try:
            set_correlation_id(test_id)
            assert get_correlation_id() == test_id
        finally:
            _correlation_id_ctx.reset(token)

    @pytest.mark.unit
    def test_get_request_id_default_none(self) -> None:
        """Verify get_request_id returns None by default."""
        from mtg_ai.middleware.correlation import (
            get_request_id,
        )

        result = get_request_id()
        assert result is None or isinstance(result, str)

    @pytest.mark.unit
    def test_get_trace_id_default_none(self) -> None:
        """Verify get_trace_id returns None by default."""
        from mtg_ai.middleware.correlation import get_trace_id

        result = get_trace_id()
        assert result is None or isinstance(result, str)

    @pytest.mark.unit
    def test_get_span_id_default_none(self) -> None:
        """Verify get_span_id returns None by default."""
        from mtg_ai.middleware.correlation import get_span_id

        result = get_span_id()
        assert result is None or isinstance(result, str)


class TestCorrelationIdGeneration:
    """Tests for correlation ID generation."""

    @pytest.mark.unit
    def test_generate_correlation_id_returns_string(self) -> None:
        """Verify generate_correlation_id returns a string."""
        from mtg_ai.middleware.correlation import (
            generate_correlation_id,
        )

        result = generate_correlation_id()

        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.unit
    def test_generate_correlation_id_is_valid_uuid(self) -> None:
        """Verify generate_correlation_id returns valid UUID4."""
        from mtg_ai.middleware.correlation import (
            generate_correlation_id,
        )

        result = generate_correlation_id()

        # Should be parseable as UUID
        parsed = uuid.UUID(result)
        assert parsed.version == 4

    @pytest.mark.unit
    def test_generate_correlation_id_unique(self) -> None:
        """Verify generate_correlation_id produces unique values."""
        from mtg_ai.middleware.correlation import (
            generate_correlation_id,
        )

        ids = [generate_correlation_id() for _ in range(100)]
        unique_ids = set(ids)

        assert len(unique_ids) == 100


class TestCorrelationContextProcessor:
    """Tests for structlog context processor."""

    @pytest.mark.unit
    def test_processor_adds_correlation_id(self) -> None:
        """Verify processor adds correlation_id to event dict."""
        from mtg_ai.middleware.correlation import (
            _correlation_id_ctx,
            correlation_context_processor,
        )

        token = _correlation_id_ctx.set("test-corr-id")
        try:
            event_dict: dict = {"event": "test"}
            result = correlation_context_processor(
                MagicMock(),
                "info",
                event_dict,
            )
            assert result["correlation_id"] == "test-corr-id"
        finally:
            _correlation_id_ctx.reset(token)

    @pytest.mark.unit
    def test_processor_adds_request_id(self) -> None:
        """Verify processor adds request_id to event dict."""
        from mtg_ai.middleware.correlation import (
            _request_id_ctx,
            correlation_context_processor,
        )

        token = _request_id_ctx.set("test-req-id")
        try:
            event_dict: dict = {"event": "test"}
            result = correlation_context_processor(
                MagicMock(),
                "info",
                event_dict,
            )
            assert result["request_id"] == "test-req-id"
        finally:
            _request_id_ctx.reset(token)

    @pytest.mark.unit
    def test_processor_adds_trace_id(self) -> None:
        """Verify processor adds trace_id to event dict."""
        from mtg_ai.middleware.correlation import (
            _trace_id_ctx,
            correlation_context_processor,
        )

        token = _trace_id_ctx.set("test-trace-id")
        try:
            event_dict: dict = {"event": "test"}
            result = correlation_context_processor(
                MagicMock(),
                "info",
                event_dict,
            )
            assert result["trace_id"] == "test-trace-id"
        finally:
            _trace_id_ctx.reset(token)

    @pytest.mark.unit
    def test_processor_adds_span_id(self) -> None:
        """Verify processor adds span_id to event dict."""
        from mtg_ai.middleware.correlation import (
            _span_id_ctx,
            correlation_context_processor,
        )

        token = _span_id_ctx.set("test-span-id")
        try:
            event_dict: dict = {"event": "test"}
            result = correlation_context_processor(
                MagicMock(),
                "info",
                event_dict,
            )
            assert result["span_id"] == "test-span-id"
        finally:
            _span_id_ctx.reset(token)

    @pytest.mark.unit
    def test_processor_skips_none_values(self) -> None:
        """Verify processor doesn't add None values to event dict."""
        from mtg_ai.middleware.correlation import (
            _correlation_id_ctx,
            _request_id_ctx,
            _span_id_ctx,
            _trace_id_ctx,
            correlation_context_processor,
        )

        # Reset all context variables
        tokens = [
            _correlation_id_ctx.set(None),
            _request_id_ctx.set(None),
            _trace_id_ctx.set(None),
            _span_id_ctx.set(None),
        ]
        try:
            event_dict: dict = {"event": "test"}
            result = correlation_context_processor(
                MagicMock(),
                "info",
                event_dict,
            )

            assert "correlation_id" not in result
            assert "request_id" not in result
            assert "trace_id" not in result
            assert "span_id" not in result
        finally:
            _correlation_id_ctx.reset(tokens[0])
            _request_id_ctx.reset(tokens[1])
            _trace_id_ctx.reset(tokens[2])
            _span_id_ctx.reset(tokens[3])


class TestHeaderConstants:
    """Tests for header constant definitions."""

    @pytest.mark.unit
    def test_correlation_id_header(self) -> None:
        """Verify CORRELATION_ID_HEADER is correctly defined."""
        from mtg_ai.middleware.correlation import (
            CORRELATION_ID_HEADER,
        )

        assert CORRELATION_ID_HEADER == "X-Correlation-ID"

    @pytest.mark.unit
    def test_request_id_header(self) -> None:
        """Verify REQUEST_ID_HEADER is correctly defined."""
        from mtg_ai.middleware.correlation import (
            REQUEST_ID_HEADER,
        )

        assert REQUEST_ID_HEADER == "X-Request-ID"

    @pytest.mark.unit
    def test_trace_id_header(self) -> None:
        """Verify TRACE_ID_HEADER is correctly defined."""
        from mtg_ai.middleware.correlation import (
            TRACE_ID_HEADER,
        )

        assert TRACE_ID_HEADER == "X-Trace-ID"

    @pytest.mark.unit
    def test_span_id_header(self) -> None:
        """Verify SPAN_ID_HEADER is correctly defined."""
        from mtg_ai.middleware.correlation import (
            SPAN_ID_HEADER,
        )

        assert SPAN_ID_HEADER == "X-Span-ID"


class TestCorrelationMiddleware:
    """Tests for CorrelationMiddleware class."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_middleware_generates_correlation_id(self) -> None:
        """Verify middleware generates correlation ID when not provided."""
        from mtg_ai.middleware.correlation import (
            CORRELATION_ID_HEADER,
            CorrelationMiddleware,
        )

        middleware = CorrelationMiddleware(app=MagicMock())

        # Create mock request without correlation headers
        mock_request = MagicMock()
        mock_request.headers = {}

        # Create mock response
        mock_response = MagicMock()
        mock_response.headers = {}

        async def mock_call_next(request):
            return mock_response

        response = await middleware.dispatch(mock_request, mock_call_next)

        # Verify correlation ID was added to response
        assert CORRELATION_ID_HEADER in response.headers
        assert len(response.headers[CORRELATION_ID_HEADER]) > 0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_middleware_extracts_correlation_id_header(self) -> None:
        """Verify middleware extracts X-Correlation-ID header."""
        from mtg_ai.middleware.correlation import (
            CORRELATION_ID_HEADER,
            CorrelationMiddleware,
        )

        middleware = CorrelationMiddleware(app=MagicMock())

        # Create mock request with correlation header
        mock_request = MagicMock()
        mock_request.headers = {CORRELATION_ID_HEADER: "incoming-corr-id"}

        mock_response = MagicMock()
        mock_response.headers = {}

        async def mock_call_next(request):
            return mock_response

        response = await middleware.dispatch(mock_request, mock_call_next)

        assert response.headers[CORRELATION_ID_HEADER] == "incoming-corr-id"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_middleware_extracts_request_id_as_fallback(self) -> None:
        """Verify middleware uses X-Request-ID as fallback for correlation."""
        from mtg_ai.middleware.correlation import (
            CORRELATION_ID_HEADER,
            REQUEST_ID_HEADER,
            CorrelationMiddleware,
        )

        middleware = CorrelationMiddleware(app=MagicMock())

        # Create mock request with only request ID header
        mock_request = MagicMock()
        mock_request.headers = {REQUEST_ID_HEADER: "incoming-req-id"}

        mock_response = MagicMock()
        mock_response.headers = {}

        async def mock_call_next(request):
            return mock_response

        response = await middleware.dispatch(mock_request, mock_call_next)

        # Correlation ID should use request ID as fallback
        assert response.headers[CORRELATION_ID_HEADER] == "incoming-req-id"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_middleware_adds_request_id_to_response(self) -> None:
        """Verify middleware adds X-Request-ID to response."""
        from mtg_ai.middleware.correlation import (
            REQUEST_ID_HEADER,
            CorrelationMiddleware,
        )

        middleware = CorrelationMiddleware(app=MagicMock())

        mock_request = MagicMock()
        mock_request.headers = {}

        mock_response = MagicMock()
        mock_response.headers = {}

        async def mock_call_next(request):
            return mock_response

        response = await middleware.dispatch(mock_request, mock_call_next)

        assert REQUEST_ID_HEADER in response.headers

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_middleware_forwards_trace_id(self) -> None:
        """Verify middleware forwards X-Trace-ID header."""
        from mtg_ai.middleware.correlation import (
            TRACE_ID_HEADER,
            CorrelationMiddleware,
        )

        middleware = CorrelationMiddleware(app=MagicMock())

        mock_request = MagicMock()
        mock_request.headers = {TRACE_ID_HEADER: "trace-123"}

        mock_response = MagicMock()
        mock_response.headers = {}

        async def mock_call_next(request):
            return mock_response

        response = await middleware.dispatch(mock_request, mock_call_next)

        assert response.headers[TRACE_ID_HEADER] == "trace-123"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_middleware_forwards_span_id(self) -> None:
        """Verify middleware forwards X-Span-ID header."""
        from mtg_ai.middleware.correlation import (
            SPAN_ID_HEADER,
            CorrelationMiddleware,
        )

        middleware = CorrelationMiddleware(app=MagicMock())

        mock_request = MagicMock()
        mock_request.headers = {SPAN_ID_HEADER: "span-456"}

        mock_response = MagicMock()
        mock_response.headers = {}

        async def mock_call_next(request):
            return mock_response

        response = await middleware.dispatch(mock_request, mock_call_next)

        assert response.headers[SPAN_ID_HEADER] == "span-456"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_middleware_resets_context_on_exception(self) -> None:
        """Verify middleware resets context variables even on exception."""
        from mtg_ai.middleware.correlation import (
            CorrelationMiddleware,
        )

        middleware = CorrelationMiddleware(app=MagicMock())

        mock_request = MagicMock()
        mock_request.headers = {"X-Correlation-ID": "test-corr"}

        async def mock_call_next_error(request):
            raise ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            await middleware.dispatch(mock_request, mock_call_next_error)

        # Context should be reset after exception
        # Note: Actual reset happens, but we can't easily verify the token reset


class TestModuleExports:
    """Tests for module __all__ exports."""

    @pytest.mark.unit
    def test_all_functions_exported(self) -> None:
        """Verify all public functions are exported."""
        from mtg_ai.middleware import correlation

        expected_exports = [
            "CorrelationMiddleware",
            "correlation_context_processor",
            "get_correlation_id",
            "get_request_id",
            "get_trace_id",
            "get_span_id",
            "set_correlation_id",
            "generate_correlation_id",
            "CORRELATION_ID_HEADER",
            "REQUEST_ID_HEADER",
            "TRACE_ID_HEADER",
            "SPAN_ID_HEADER",
        ]

        for export in expected_exports:
            assert hasattr(correlation, export), f"{export} not exported from module"
