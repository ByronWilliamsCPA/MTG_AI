"""Health check endpoints for Kubernetes and production monitoring.

This module provides standardized health check endpoints following best practices:
- Liveness probe: Is the application running?
- Readiness probe: Can the application serve traffic?
- Startup probe: Has the application fully started?

Implements:
- Kubernetes probe patterns
- Graceful degradation
- Detailed diagnostic information
- OWASP A09 (Security Logging) compliance
"""

from __future__ import annotations

import sys
import time

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

router = APIRouter(prefix="/health", tags=["health"])

# Track application start time for uptime calculation
_START_TIME = time.time()


class HealthStatus(BaseModel):
    """Health check response model."""

    status: str = Field(..., description="Overall status: ok, degraded, or error")
    timestamp: float = Field(default_factory=time.time, description="Unix timestamp")
    uptime_seconds: float = Field(..., description="Application uptime in seconds")
    version: str = Field(default="0.1.0", description="Application version")
    python_version: str = Field(default_factory=lambda: sys.version.split()[0])


class ReadinessCheck(BaseModel):
    """Individual dependency check result."""

    name: str = Field(..., description="Dependency name")
    status: bool = Field(..., description="Check passed")
    latency_ms: float | None = Field(None, description="Check latency in milliseconds")
    error: str | None = Field(None, description="Error message if failed")


class ReadinessStatus(HealthStatus):
    """Readiness check response with dependency details."""

    checks: dict[str, ReadinessCheck] = Field(
        default_factory=dict, description="Individual dependency checks"
    )


@router.get(
    "/live",
    response_model=HealthStatus,
    status_code=status.HTTP_200_OK,
    summary="Liveness probe",
    description="Indicates if the application is running. Used by Kubernetes liveness probe.",
)
async def liveness() -> HealthStatus:
    """Kubernetes liveness probe.

    Returns HTTP 200 if the application is alive.
    If this fails, Kubernetes will restart the pod.

    This should be a simple, fast check that doesn't depend on external services.
    """
    return HealthStatus(
        status="ok",
        uptime_seconds=time.time() - _START_TIME,
    )


async def check_database() -> ReadinessCheck:
    """Check database connectivity.

    Returns:
        ReadinessCheck with database status and latency
    """
    start = time.time()
    try:
        # Import here to avoid circular dependencies
        from mtg_ai.core.database import get_session

        async with get_session() as session:
            # Simple query to check connectivity
            await session.execute("SELECT 1")

        latency_ms = (time.time() - start) * 1000
        return ReadinessCheck(
            name="database",
            status=True,
            latency_ms=round(latency_ms, 2),
        )
    except Exception as e:
        latency_ms = (time.time() - start) * 1000
        return ReadinessCheck(
            name="database",
            status=False,
            latency_ms=round(latency_ms, 2),
            error=str(e),
        )


async def check_cache() -> ReadinessCheck:
    """Check Redis/cache connectivity.

    Returns:
        ReadinessCheck with cache status and latency
    """
    start = time.time()
    try:
        # Example Redis check - adjust based on your cache implementation
        # from mtg_ai.core.cache import redis_client
        # await redis_client.ping()

        # Placeholder - replace with actual cache check
        latency_ms = (time.time() - start) * 1000
        return ReadinessCheck(
            name="cache",
            status=True,
            latency_ms=round(latency_ms, 2),
        )
    except Exception as e:
        latency_ms = (time.time() - start) * 1000
        return ReadinessCheck(
            name="cache",
            status=False,
            latency_ms=round(latency_ms, 2),
            error=str(e),
        )


async def check_external_service() -> ReadinessCheck:
    """Check external API/service connectivity.

    Returns:
        ReadinessCheck with external service status
    """
    start = time.time()
    try:
        # Example external service check
        # import httpx
        # async with httpx.AsyncClient() as client:
        #     response = await client.get("https://api.example.com/health", timeout=2.0)
        #     response.raise_for_status()

        # Placeholder - replace with actual external service check
        latency_ms = (time.time() - start) * 1000
        return ReadinessCheck(
            name="external_api",
            status=True,
            latency_ms=round(latency_ms, 2),
        )
    except Exception as e:
        latency_ms = (time.time() - start) * 1000
        return ReadinessCheck(
            name="external_api",
            status=False,
            latency_ms=round(latency_ms, 2),
            error=str(e),
        )


@router.get(
    "/ready",
    response_model=ReadinessStatus,
    responses={
        200: {"description": "Application is ready to serve traffic"},
        503: {"description": "Application is not ready (dependencies unavailable)"},
    },
    summary="Readiness probe",
    description="Checks if the application can serve traffic. Used by Kubernetes readiness probe.",
)
async def readiness() -> ReadinessStatus:
    """Kubernetes readiness probe.

    Checks all critical dependencies:
    - Database connectivity
    - Cache availability (if configured)
    - External service health (if applicable)

    Returns HTTP 503 if any critical dependency is unavailable.
    If this fails, Kubernetes will stop sending traffic to this pod.
    """
    checks: dict[str, ReadinessCheck] = {}

    # Run all checks in parallel for better performance
    # For now, run sequentially - can be optimized with asyncio.gather()
    checks["database"] = await check_database()
    # Uncomment if using cache:
    # checks["cache"] = await check_cache()

    # Uncomment if checking external services:
    # checks["external_api"] = await check_external_service()

    # Determine overall status
    all_healthy = all(check.status for check in checks.values())

    if not all_healthy:
        # Return 503 if any critical check fails
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "unavailable",
                "timestamp": time.time(),
                "uptime_seconds": time.time() - _START_TIME,
                "checks": {name: check.model_dump() for name, check in checks.items()},
            },
        )

    return ReadinessStatus(
        status="ok",
        uptime_seconds=time.time() - _START_TIME,
        checks=checks,
    )


@router.get(
    "/startup",
    response_model=HealthStatus,
    status_code=status.HTTP_200_OK,
    summary="Startup probe",
    description="Indicates if the application has completed startup. Used by Kubernetes startup probe.",
)
async def startup() -> HealthStatus:
    """Kubernetes startup probe.

    Used during application startup to delay liveness and readiness checks.
    This prevents the application from being killed during slow initialization.

    Returns HTTP 200 once the application has fully started.
    """
    # Add any startup checks here (e.g., database migrations completed)
    # For most applications, being alive means startup is complete

    return HealthStatus(
        status="started",
        uptime_seconds=time.time() - _START_TIME,
    )


@router.get(
    "/",
    response_model=HealthStatus,
    status_code=status.HTTP_200_OK,
    summary="Basic health check",
    description="Simple health check endpoint for load balancers and monitoring.",
    include_in_schema=False,  # Hide from OpenAPI docs (use /live instead)
)
async def health() -> HealthStatus:
    """Basic health check endpoint.

    Alias for /health/live for compatibility with load balancers
    that expect a /health endpoint.
    """
    return await liveness()


# =============================================================================
# Kubernetes Probe Configuration Examples
# =============================================================================
"""
Add to your Kubernetes Deployment YAML:

apiVersion: apps/v1
kind: Deployment
metadata:
  name: mtg_ai
spec:
  template:
    spec:
      containers:
      - name: app
        image: mtg_ai:latest
        ports:
        - containerPort: 8000

        # Liveness probe - restart if fails
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 3
          failureThreshold: 3

        # Readiness probe - stop traffic if fails
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3

        # Startup probe - delay other probes during startup
        startupProbe:
          httpGet:
            path: /health/startup
            port: 8000
          initialDelaySeconds: 0
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 30  # 30 * 5s = 150s max startup time
"""
