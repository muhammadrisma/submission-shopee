#!/usr/bin/env python3
"""
Local CI testing script to simulate CI/CD pipeline checks locally.
This helps developers test their changes before pushing to the repository.
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(command: str, description: str) -> bool:
    """Run a command and return success status."""
    print(f"\n🔄 {description}")
    print(f"Running: {command}")
    print("-" * 50)

    try:
        result = subprocess.run(
            command, shell=True, check=True, capture_output=False, text=True
        )
        print(f"✅ {description} - PASSED")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED")
        print(f"Exit code: {e.returncode}")
        return False


def check_requirements():
    """Check if required tools are installed."""
    tools = {
        "python": "python --version",
        "docker": "docker --version",
        "pip": "pip --version",
    }

    missing_tools = []
    for tool, command in tools.items():
        try:
            subprocess.run(command, shell=True, check=True, capture_output=True)
            print(f"✅ {tool} is available")
        except subprocess.CalledProcessError:
            print(f"❌ {tool} is not available")
            missing_tools.append(tool)

    if missing_tools:
        print(f"\nMissing required tools: {', '.join(missing_tools)}")
        return False

    return True


def main():
    print("🚀 Local CI/CD Pipeline Test")
    print("=" * 50)

    # Check if we're in the right directory
    if not Path("requirements.txt").exists():
        print("❌ Please run this script from the project root directory")
        sys.exit(1)

    # Check requirements
    if not check_requirements():
        print("\n❌ Missing required tools. Please install them first.")
        sys.exit(1)

    # Install development dependencies
    print("\n📦 Installing development dependencies...")
    if not run_command(
        "pip install -r requirements-dev.txt", "Install development dependencies"
    ):
        sys.exit(1)

    # Code quality checks
    checks = [
        ("black --check --diff .", "Code formatting check (Black)"),
        ("isort --check-only --diff .", "Import sorting check (isort)"),
        (
            "flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics",
            "Syntax error check (flake8)",
        ),
        ("bandit -r . -ll", "Security check (bandit)"),
        ("safety check", "Dependency security check (safety)"),
    ]

    failed_checks = []
    for command, description in checks:
        if not run_command(command, description):
            failed_checks.append(description)

    # Run tests if available
    if Path("tests").exists():
        if not run_command(
            "pytest --cov=. --cov-report=term", "Run tests with coverage"
        ):
            failed_checks.append("Tests")

    # Docker build test
    if not run_command("docker build -t local-test .", "Docker build test"):
        failed_checks.append("Docker build")

    # Summary
    print("\n" + "=" * 50)
    print("📊 LOCAL CI/CD TEST SUMMARY")
    print("=" * 50)

    if failed_checks:
        print("❌ FAILED CHECKS:")
        for check in failed_checks:
            print(f"  - {check}")
        print("\n💡 Fix the issues above before pushing to the repository.")
        sys.exit(1)
    else:
        print("🎉 ALL CHECKS PASSED!")
        print("✅ Your code is ready to be pushed to the repository.")
        print("\n🚀 Next steps:")
        print("  1. git add .")
        print("  2. git commit -m 'Your commit message'")
        print("  3. git push")


if __name__ == "__main__":
    main()
