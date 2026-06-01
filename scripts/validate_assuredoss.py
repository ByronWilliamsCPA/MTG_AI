#!/usr/bin/env python
"""---
title: "Validate Assured OSS Credentials"
name: "validate_assuredoss.py"
description: "Validates ADC for Assured OSS and lists available packages."
category: script
usage: "uv run python scripts/validate_assuredoss.py"
behavior: "Checks ADC credentials and enumerates OSS packages"
inputs: "GOOGLE_APPLICATION_CREDENTIALS, GOOGLE_CLOUD_PROJECT"
outputs: "Console output of credential path, project ID, and package list"
dependencies: "google-auth, google-cloud-assuredoss, google-api-core, python-dotenv"
author: "Byron Williams"
last_modified: "2026-06-01"
changelog: "Add front-matter metadata and module docstring"
tags: [scripts, tools, assuredoss, validation]
---

Module: validate_assuredoss

This script verifies that Google Application Default Credentials (ADC)
are correctly configured for Assured OSS, and lists available OSS packages
for the configured project.

Functions:
    main(): Entry point for credential validation and package listing.
    setup_credentials(): Decode and setup credentials from environment.
"""

import base64
import json
import os
import tempfile
from pathlib import Path

from dotenv import load_dotenv
from google.api_core.exceptions import GoogleAPICallError
from google.auth.exceptions import DefaultCredentialsError
from google.cloud.assuredoss import V1Client


def setup_credentials() -> None:
    """Set up Google Cloud credentials from environment variables.

    Handles both file-based credentials (GOOGLE_APPLICATION_CREDENTIALS)
    and base64-encoded credentials (GOOGLE_APPLICATION_CREDENTIALS_B64).

    For CI/CD environments, base64 encoding is preferred:
        base64 -w 0 service-account-key.json

    Raises:
        ValueError: If neither credential method is configured.
    """
    # Check if credentials are already set via file path
    if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        print(
            "✅ Using credentials from file:",
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"],
        )
        return

    # Try to use base64-encoded credentials
    cred_b64 = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS_B64")
    if not cred_b64:
        msg = (
            "❌ No credentials found. Set either:\n"
            "   GOOGLE_APPLICATION_CREDENTIALS (file path)\n"
            "   GOOGLE_APPLICATION_CREDENTIALS_B64 (base64 encoded JSON)"
        )
        raise ValueError(msg)

    # Decode base64 credentials and write to temp file
    try:
        cred_json = base64.b64decode(cred_b64).decode("utf-8")
        json.loads(cred_json)  # Validate JSON

        # Write to temporary file
        temp_cred_file = Path(tempfile.gettempdir()) / "gcp-credentials.json"
        temp_cred_file.write_text(cred_json)
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(temp_cred_file)

        print(f"✅ Using base64-encoded credentials (temp file: {temp_cred_file})")

    except (base64.binascii.Error, UnicodeDecodeError, json.JSONDecodeError) as e:
        msg = f"❌ Invalid base64 credentials: {e}"
        raise ValueError(msg) from e


def main() -> None:
    """Validate ADC credentials and list Assured OSS packages.

    Reads the `GOOGLE_APPLICATION_CREDENTIALS` and
    `GOOGLE_CLOUD_PROJECT` environment variables, initializes the
    Assured OSS client, and prints the retrieved package list.

    Raises:
        DefaultCredentialsError: If ADC cannot be loaded.
        GoogleAPICallError: If the API call fails.
        ValueError: If required environment variables are missing.
    """
    # Load environment variables from .env file
    load_dotenv()

    try:
        # Setup credentials (from file or base64)
        setup_credentials()

        # Validate required environment variables
        project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
        if not project_id:
            raise ValueError("❌ GOOGLE_CLOUD_PROJECT not set")

        use_assured_oss = os.environ.get("USE_ASSURED_OSS", "true").lower() == "true"
        region = os.environ.get("ASSURED_OSS_REGION", "us")
        repository = os.environ.get("ASSURED_OSS_REPOSITORY", "assuredoss")

        print("\n" + "=" * 70)
        print("🔐 Google Assured OSS Validation")
        print("=" * 70)
        print(f"📦 Project:    {project_id}")
        print(f"🌍 Region:     {region}")
        print(f"📚 Repository: {repository}")
        print(f"✨ Enabled:    {use_assured_oss}")
        print("=" * 70 + "\n")

        if not use_assured_oss:
            print("⚠️  Assured OSS is disabled (USE_ASSURED_OSS=false)")
            print("📦 Using PyPI as the only package source")
            return

        # Initialize Assured OSS client
        client = V1Client()

        # List available packages
        print("🔍 Connecting to Assured OSS...")
        response = client.list_packages()

        print(f"✅ Connected! Found {len(response.packages)} packages:\n")

        # Display packages in a formatted way
        for i, pkg in enumerate(response.packages, 1):
            version = getattr(pkg, "version", "unknown")
            print(f"  {i:3d}. {pkg.name:40s} (v{version})")

        print("\n" + "=" * 70)
        print(f"✅ Validation successful! Total packages: {len(response.packages)}")
        print("=" * 70)

    except ValueError as e:
        print(f"\n{e}\n")
        print("💡 Setup Instructions:")
        print("   1. Copy .env.example to .env")
        print("   2. Set GOOGLE_CLOUD_PROJECT to your GCP project ID")
        print("   3. Set up credentials (one of the following):")
        print("      a) GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json")
        print("      b) GOOGLE_APPLICATION_CREDENTIALS_B64=<base64-encoded-json>")
        raise

    except DefaultCredentialsError as e:
        print(f"❌ Could not load credentials: {e}")
        print("\n💡 Troubleshooting:")
        print("   - Verify your service account JSON is valid")
        print("   - Check that the service account has 'Artifact Registry Reader' role")
        print("   - Ensure GOOGLE_APPLICATION_CREDENTIALS points to the right file")
        raise

    except GoogleAPICallError as e:
        print(f"❌ Failed to list packages: {e}")
        print("\n💡 Troubleshooting:")
        print("   - Verify your GCP project ID is correct")
        print("   - Check that Assured OSS is enabled in your project")
        print("   - Ensure the service account has proper permissions")
        raise


if __name__ == "__main__":
    main()
