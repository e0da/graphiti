#!/usr/bin/env python3
"""Test runner for Graphiti MCP Server tests."""

import sys
import subprocess
import argparse
from pathlib import Path


def main():
    """Run the test suite."""
    parser = argparse.ArgumentParser(description="Run Graphiti MCP Server tests")
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Run tests in verbose mode"
    )
    parser.add_argument(
        "--test", "-t",
        help="Run specific test file (e.g., test_episode_processing_bug.py)"
    )
    parser.add_argument(
        "--check-services",
        action="store_true",
        help="Check if Docker services are running before running tests"
    )
    parser.add_argument(
        "--unit-only",
        action="store_true",
        help="Run only unit tests (no external dependencies)"
    )
    parser.add_argument(
        "--integration-only",
        action="store_true",
        help="Run only integration tests (requires external services)"
    )

    args = parser.parse_args()

    # Change to the project directory
    project_dir = Path(__file__).parent
    print(f"Running tests in: {project_dir}")

    # Check if services are running (optional)
    if args.check_services:
        print("Checking Docker services...")
        try:
            result = subprocess.run(
                ["docker", "compose", "ps", "--services", "--filter", "status=running"],
                capture_output=True,
                text=True,
                check=True,
                cwd=project_dir
            )
            running_services = result.stdout.strip().split('\n')
            if 'neo4j' not in running_services or 'graphiti-mcp' not in running_services:
                print("❌ Required services are not running. Start them with: docker compose up -d")
                return 1
            print("✅ Docker services are running")
        except subprocess.CalledProcessError:
            print("❌ Failed to check Docker services")
            return 1

    # Run tests
    try:
        if args.unit_only:
            print("Running unit tests only...")
            cmd = ["python", "-m", "unittest", "discover", "-s", "tests/unit"]
        elif args.integration_only:
            print("Running integration tests only...")
            cmd = ["python", "-m", "unittest", "discover", "-s", "tests/integration"]
        else:
            cmd = ["python", "-m", "unittest"]

            if args.verbose:
                cmd.append("-v")

            if args.test:
                # Convert test file name to module name
                test_module = args.test.replace(".py", "").replace("/", ".")
                cmd.append(f"tests.{test_module}")
            else:
                cmd.append("discover")
                cmd.append("-s")
                cmd.append("tests")

        if args.verbose and not (args.unit_only or args.integration_only):
            cmd.append("-v")

        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, cwd=project_dir)

        if result.returncode == 0:
            print("✅ All tests passed!")
        else:
            print("❌ Some tests failed")

    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return 1

    return result.returncode if 'result' in locals() else 0


if __name__ == "__main__":
    sys.exit(main())
