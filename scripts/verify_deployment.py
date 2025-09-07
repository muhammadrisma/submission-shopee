#!/usr/bin/env python3
"""
Deployment verification script for Food Receipt Analyzer.
This script performs basic health checks on the deployed application.
"""

import argparse
import sys
import time
from typing import Any, Dict

import requests


def check_health_endpoint(base_url: str, timeout: int = 30) -> bool:
    """Check if the Streamlit health endpoint is responding."""
    health_url = f"{base_url}/_stcore/health"

    for attempt in range(timeout):
        try:
            response = requests.get(health_url, timeout=5)
            if response.status_code == 200:
                print(f"✅ Health check passed (attempt {attempt + 1})")
                return True
        except requests.RequestException as e:
            print(f"⏳ Health check attempt {attempt + 1} failed: {e}")

        if attempt < timeout - 1:
            time.sleep(1)

    print(f"❌ Health check failed after {timeout} attempts")
    return False


def check_main_page(base_url: str) -> bool:
    """Check if the main page loads successfully."""
    try:
        response = requests.get(base_url, timeout=10)
        if response.status_code == 200:
            print("✅ Main page is accessible")
            return True
        else:
            print(f"❌ Main page returned status code: {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"❌ Failed to access main page: {e}")
        return False


def check_static_resources(base_url: str) -> bool:
    """Check if static resources are loading."""
    static_endpoints = [
        "/_stcore/static/css/bootstrap.min.css",
        "/_stcore/static/js/bootstrap.bundle.min.js",
    ]

    success_count = 0
    for endpoint in static_endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                success_count += 1
                print(f"✅ Static resource accessible: {endpoint}")
            else:
                print(
                    f"⚠️ Static resource issue: {endpoint} (status: {response.status_code})"
                )
        except requests.RequestException as e:
            print(f"⚠️ Static resource error: {endpoint} - {e}")

    if success_count > 0:
        print(f"✅ {success_count}/{len(static_endpoints)} static resources accessible")
        return True
    else:
        print("❌ No static resources accessible")
        return False


def run_deployment_verification(base_url: str, timeout: int = 30) -> Dict[str, Any]:
    """Run all deployment verification checks."""
    print(f"🚀 Starting deployment verification for: {base_url}")
    print("=" * 50)

    results = {
        "health_check": False,
        "main_page": False,
        "static_resources": False,
        "overall_success": False,
    }

    print("1. Checking health endpoint...")
    results["health_check"] = check_health_endpoint(base_url, timeout)

    print("\n2. Checking main page accessibility...")
    results["main_page"] = check_main_page(base_url)

    print("\n3. Checking static resources...")
    results["static_resources"] = check_static_resources(base_url)

    results["overall_success"] = results["health_check"] and results["main_page"]

    print("\n" + "=" * 50)
    if results["overall_success"]:
        print("🎉 Deployment verification PASSED!")
        print("The application is ready for use.")
    else:
        print("❌ Deployment verification FAILED!")
        print("Please check the application logs and configuration.")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Verify Food Receipt Analyzer deployment"
    )
    parser.add_argument(
        "--url",
        default="http://localhost:8501",
        help="Base URL of the application (default: http://localhost:8501)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Timeout in seconds for health checks (default: 30)",
    )
    parser.add_argument(
        "--exit-on-failure",
        action="store_true",
        help="Exit with non-zero code if verification fails",
    )

    args = parser.parse_args()

    results = run_deployment_verification(args.url, args.timeout)

    if args.exit_on_failure and not results["overall_success"]:
        sys.exit(1)

    return results


if __name__ == "__main__":
    main()
