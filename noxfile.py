"""Nox-UV sessions for testing, documentation, and compliance workflows.

Nox-UV uses UV for fast virtual environment creation and package installation.
This file defines sessions organized by the test pyramid pattern.

Test Pyramid Sessions:
    nox -s test            # Run full test suite across Python 3.10-3.14
    nox -s unit            # Run unit tests only (fast, 85%+ coverage target)
    nox -s integration     # Run integration tests (70%+ coverage target)
    nox -s fast            # Fast dev loop - excludes slow tests
    nox -s security_tests  # Run security assertion tests
    nox -s perf            # Run performance tests (if load testing enabled)
    nox -s mutate          # Run mutation testing (if mutation testing enabled)

Code Quality Sessions:
    nox -s lint            # Run Ruff linting across Python 3.10-3.14
    nox -s typecheck       # Run MyPy type checking across Python 3.10-3.14
    nox -s docstrings      # Check docstring coverage

Documentation Sessions:
    nox -s frontmatter     # Validate and autofix front matter
    nox -s docs            # Build documentation
    nox -s serve           # Serve documentation locally
    nox -s validate        # Run all documentation validation checks

Compliance Sessions:
    nox -s reuse           # Check REUSE compliance
    nox -s sbom            # Generate SBOM
    nox -s scan            # Scan SBOM for vulnerabilities
    nox -s compliance      # Run all compliance checks
    nox -s assuredoss      # Validate Google Assured OSS credentials
"""

# nox-uv is imported but not explicitly registered.
# In nox-uv 0.6.x+, registration happens automatically when using
# the "uv" backend specified in nox.options.default_venv_backend
import contextlib

import nox

with contextlib.suppress(ImportError):
    import nox_uv  # noqa: F401 - Required for uv backend support

# Default sessions and options
nox.options.sessions = ["test", "lint", "docs"]
nox.options.reuse_existing_virtualenvs = True
nox.options.default_venv_backend = "uv"


@nox.session(python="3.12")
def frontmatter(session: nox.Session) -> None:
    """Validate and autofix front matter in documentation.

    This session installs the required dependencies and runs the front matter
    validation script with autofix enabled.
    """
    session.install("pydantic>=2.0", "python-frontmatter>=1.1", "ruamel.yaml>=0.18")
    session.run("python", "tools/validate_front_matter.py", "docs", "--fix")


@nox.session(python="3.12")
def docs(session: nox.Session) -> None:
    """Build documentation with MkDocs.

    This session installs the project with docs dependencies and builds
    the documentation in strict mode.
    """
    session.install("-e", ".[dev]")
    session.run("mkdocs", "build", "--strict")


@nox.session(python="3.12")
def serve(session: nox.Session) -> None:
    """Serve documentation locally for development.

    This session starts the MkDocs development server with live reloading.
    Access at http://127.0.0.1:8000
    """
    session.install("-e", ".[dev]")
    session.run("mkdocs", "serve")


@nox.session(python="3.12")
def docstrings(session: nox.Session) -> None:
    """Check docstring coverage with interrogate and pydocstyle.

    This session validates that docstrings meet the Google style convention
    and that coverage meets the minimum threshold.
    """
    session.install("pydocstyle>=6.3", "interrogate>=1.7")
    session.run("pydocstyle", "src/")
    session.run("interrogate", "-c", "pyproject.toml", "src/")


@nox.session(python="3.12")
def validate(session: nox.Session) -> None:
    """Run all validation checks for documentation.

    This session combines front matter validation, docstring checks,
    and documentation building to ensure everything is correct.
    """
    session.install(
        "-e",
        ".[dev]",
        "pydantic>=2.0",
        "python-frontmatter>=1.1",
        "ruamel.yaml>=0.18",
        "pydocstyle>=6.3",
        "interrogate>=1.7",
    )
    session.run("python", "tools/validate_front_matter.py", "docs", "--fix")
    session.run("pydocstyle", "src/")
    session.run("interrogate", "-c", "pyproject.toml", "src/")
    session.run("mkdocs", "build", "--strict")


@nox.session(python="3.12")
def reuse(session: nox.Session) -> None:
    """Check REUSE compliance.

    This session uses the REUSE tool to verify that all files have proper
    licensing information according to the REUSE specification.
    Requires Docker to be installed and running.
    """
    session.run(
        "docker",
        "run",
        "--rm",
        "--volume",
        f"{session.posargs[0] if session.posargs else '.'}:/data",
        "fsfe/reuse:latest",
        "lint",
        external=True,
    )


@nox.session(python="3.12")
def reuse_spdx(session: nox.Session) -> None:
    """Generate REUSE SPDX document.

    This session generates an SPDX document from the REUSE metadata.
    The SPDX file is saved to reuse-spdx.json in the current directory.
    Requires Docker to be installed and running.
    """
    session.run(
        "docker",
        "run",
        "--rm",
        "--volume",
        f"{session.posargs[0] if session.posargs else '.'}:/data",
        "fsfe/reuse:latest",
        "spdx",
        "--output",
        "/data/reuse-spdx.json",
        external=True,
    )
    session.log("SPDX document generated: reuse-spdx.json")


@nox.session(python="3.12")
def sbom(session: nox.Session) -> None:
    """Generate CycloneDX SBOM using UV.

    This session generates Software Bill of Materials (SBOM) in CycloneDX format
    for runtime and development dependency sets using UV's pip-compatible interface.
    """
    session.install("cyclonedx-bom==4.6.1")

    # Generate runtime SBOM (production dependencies only)
    # Export production dependencies to requirements.txt format
    session.run(
        "uv",
        "pip",
        "compile",
        "pyproject.toml",
        "--output-file",
        "requirements-runtime.txt",
        "--no-dev",
        external=True,
    )
    session.run(
        "cyclonedx-py",
        "requirements",
        "requirements-runtime.txt",
        "--of",
        "json",
        "-o",
        "sbom-runtime.json",
    )
    session.log("Runtime SBOM generated: sbom-runtime.json")

    # Generate development SBOM (all dependencies including dev)
    session.run(
        "uv",
        "export",
        "--format",
        "requirements-txt",
        "--output-file",
        "requirements-all.txt",
        "--no-hashes",
        external=True,
    )
    session.run(
        "cyclonedx-py",
        "requirements",
        "requirements-all.txt",
        "--of",
        "json",
        "-o",
        "sbom-complete.json",
    )
    session.log("Complete SBOM generated: sbom-complete.json")

    # Clean up temporary files
    import pathlib

    pathlib.Path("requirements-runtime.txt").unlink(missing_ok=True)
    pathlib.Path("requirements-all.txt").unlink(missing_ok=True)


@nox.session(python="3.12")
def scan(session: nox.Session) -> None:
    """Scan SBOM for vulnerabilities.

    This session uses Trivy to scan the generated SBOMs for known vulnerabilities.
    Requires Docker to be installed and running.
    Requires SBOM files to be generated first (run 'nox -s sbom').
    """
    import pathlib

    sbom_file = session.posargs[0] if session.posargs else "sbom-runtime.json"

    if not pathlib.Path(sbom_file).exists():
        session.error(f"SBOM file not found: {sbom_file}. Run 'nox -s sbom' first.")

    session.run(
        "docker",
        "run",
        "--rm",
        "--volume",
        f"{pathlib.Path().absolute()}:/workspace",
        "aquasec/trivy:latest",
        "sbom",
        f"/workspace/{sbom_file}",
        "--severity",
        "CRITICAL,HIGH",
        "--format",
        "table",
        external=True,
    )


@nox.session(python="3.12")
def compliance(session: nox.Session) -> None:
    """Run all compliance checks.

    This session runs REUSE compliance checks and generates SBOMs
    for comprehensive compliance validation.
    """
    session.log("Running REUSE compliance check...")
    reuse(session)

    session.log("Generating SBOMs...")
    sbom(session)

    session.log("Scanning runtime SBOM for vulnerabilities...")
    scan(session)

    session.log("All compliance checks completed successfully!")


@nox.session(python="3.12")
def assuredoss(session: nox.Session) -> None:
    """Validate Google Assured OSS credentials and configuration.

    This session validates that:
    - Google Cloud credentials are properly configured
    - Project ID is set correctly
    - Assured OSS is accessible
    - Package listing works

    Requires .env file with:
    - GOOGLE_CLOUD_PROJECT
    - GOOGLE_APPLICATION_CREDENTIALS or GOOGLE_APPLICATION_CREDENTIALS_B64
    """
    session.install("-e", ".[dev]")
    session.run("python", "scripts/validate_assuredoss.py")


# ==========================================
# TEST PYRAMID SESSIONS
# ==========================================


@nox.session(python=["3.10", "3.11", "3.12", "3.13", "3.14"])
def test(session: nox.Session) -> None:
    """Run full test suite across multiple Python versions.

    This session runs all tests with coverage reporting
    across Python 3.10, 3.11, 3.12, 3.13, and 3.14 to ensure compatibility.
    """
    session.install("-e", ".[dev]")
    session.run(
        "pytest",
        "-v",
        "--cov=src",
        "--cov-branch",
        "--cov-report=xml:coverage.xml",
        "--cov-report=term-missing:skip-covered",
        "--cov-fail-under=80",
        "tests/",
        *session.posargs,
    )


@nox.session(python="3.12")
def unit(session: nox.Session) -> None:
    """Run unit tests only (fast development cycle).

    Unit tests are isolated, fast, and don't require external dependencies.
    Target: 85%+ coverage for unit tests.
    """
    session.install("-e", ".[dev]")
    session.run(
        "pytest",
        "-m",
        "unit and not slow",
        "--cov=src",
        "--cov-branch",
        "--cov-report=xml:coverage-unit.xml",
        "--cov-report=term-missing:skip-covered",
        "--cov-fail-under=85",
        "-v",
        *session.posargs,
    )


@nox.session(python="3.12")
def integration(session: nox.Session) -> None:
    """Run integration tests (with real services).

    Integration tests verify interaction between components.
    Target: 70%+ coverage for integration tests.
    """
    session.install("-e", ".[dev]")
    session.run(
        "pytest",
        "-m",
        "integration",
        "--cov=src",
        "--cov-branch",
        "--cov-report=xml:coverage-integration.xml",
        "--cov-report=term-missing:skip-covered",
        "--cov-fail-under=70",
        "-v",
        *session.posargs,
    )


@nox.session(python="3.12")
def fast(session: nox.Session) -> None:
    """Fast development loop - exclude slow tests.

    Use this for rapid feedback during development.
    Excludes slow tests and stops after 5 failures.
    """
    session.install("-e", ".[dev]")
    session.run(
        "pytest",
        "-m",
        "not slow",
        "--cov=src",
        "--cov-branch",
        "--cov-report=term-missing:skip-covered",
        "--cov-fail-under=75",
        "--maxfail=5",
        "-v",
        *session.posargs,
    )


@nox.session(python="3.12")
def security_tests(session: nox.Session) -> None:
    """Run security assertion tests.

    Tests focused on security-critical functionality.
    """
    session.install("-e", ".[dev]")
    session.run(
        "pytest",
        "-m",
        "security",
        "--cov=src",
        "--cov-branch",
        "--cov-report=xml:coverage-security.xml",
        "--cov-report=term-missing:skip-covered",
        "-v",
        *session.posargs,
    )


# ==========================================
# CODE QUALITY SESSIONS
# ==========================================


@nox.session(python=["3.10", "3.11", "3.12", "3.13", "3.14"])
def lint(session: nox.Session) -> None:
    """Run linting across multiple Python versions.

    This session runs Ruff linting and type hint checks to ensure code quality
    across all supported Python versions.
    """
    session.install("-e", ".[dev]")
    session.run("ruff", "check", ".", "--config=pyproject.toml")
    session.run("ruff", "format", "--check")
    session.run("python", "scripts/check_type_hints.py", "--src-dir=src")


@nox.session(python=["3.10", "3.11", "3.12", "3.13", "3.14"])
def typecheck(session: nox.Session) -> None:
    """Run type checking across multiple Python versions.

    This session runs BasedPyright type checking to ensure type safety
    across all supported Python versions. BasedPyright is a stricter fork
    of Pyright that provides faster analysis than MyPy.
    """
    session.install("-e", ".[dev]")
    session.run("basedpyright", "src")
