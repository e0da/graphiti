"""Test configuration and utilities for Graphiti MCP Server tests."""

import os
import subprocess
from typing import Dict, Any, List


def get_test_group_id() -> str:
    """Return a test group ID for isolated testing."""
    return "test-group"


def get_default_group_id() -> str:
    """Return the default group ID configured in the server."""
    return "default"


def query_neo4j(query: str, parameters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """Execute a Cypher query against Neo4j."""
    cmd = [
        "docker", "exec", "mcp_server-neo4j-1", "cypher-shell",
        "-u", "neo4j",
        "-p", "neo4j-pw-98723lkjs98723m98uj",
        query
    ]

    if parameters:
        # Convert parameters to Cypher format - each parameter needs to be passed separately
        for key, value in parameters.items():
            cmd.extend(["--param", f"{key}: {repr(value)}"])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        # Parse the result (simplified - in real implementation would need proper parsing)
        lines = result.stdout.strip().split('\n')
        if len(lines) <= 1:  # Just headers or empty
            return []

        # Simple parsing - in real implementation would need proper CSV parsing
        headers = lines[0].split(', ')
        data = []
        for line in lines[1:]:
            if line.strip():
                values = line.split(', ')
                if len(values) == len(headers):
                    # Remove quotes from string values
                    cleaned_values = []
                    for value in values:
                        if value.startswith('"') and value.endswith('"'):
                            cleaned_values.append(value[1:-1])  # Remove quotes
                        else:
                            cleaned_values.append(value)
                    data.append(dict(zip(headers, cleaned_values)))
        return data
    except subprocess.CalledProcessError as e:
        print(f"Neo4j query failed: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return []


def get_server_logs() -> str:
    """Get server logs."""
    try:
        result = subprocess.run(
            ["docker", "compose", "logs", "graphiti-mcp"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError:
        return ""


def check_services_running() -> bool:
    """Check if Docker services are running."""
    try:
        result = subprocess.run(
            ["docker", "compose", "ps", "--services", "--filter", "status=running"],
            capture_output=True,
            text=True,
            check=True
        )
        running_services = result.stdout.strip().split('\n')
        return 'neo4j' in running_services and 'graphiti-mcp' in running_services
    except subprocess.CalledProcessError:
        return False
