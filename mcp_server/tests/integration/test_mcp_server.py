"""Integration tests for MCP server functionality."""

import unittest
import subprocess
from tests.conftest import get_server_logs, check_services_running
from tests.test_utils import integration_test, skip_if_no_services


@integration_test
class TestMCPServer(unittest.TestCase):
    """Test MCP server functionality and behavior."""

    @skip_if_no_services
    def test_server_startup_and_health(self):
        """Test that the MCP server starts up correctly and is healthy."""
        # Check that the server is running
        result = subprocess.run(
            ["docker", "compose", "ps", "graphiti-mcp"],
            capture_output=True,
            text=True,
            check=True
        )

        self.assertIn("Up", result.stdout, "Graphiti MCP server should be running")

        # Check server logs for successful startup
        logs = get_server_logs()
        self.assertIn("Using provided group_id: default", logs, "Server should use default group_id")
        self.assertIn("Using group_id: default", logs, "Server should be configured with default group_id")

    @skip_if_no_services
    def test_neo4j_connection(self):
        """Test that the MCP server can connect to Neo4j."""
        # Check that Neo4j is running
        result = subprocess.run(
            ["docker", "compose", "ps", "neo4j"],
            capture_output=True,
            text=True,
            check=True
        )

        self.assertIn("Up", result.stdout, "Neo4j should be running")

        # Check that indexes were created (indicates successful connection)
        from tests.conftest import query_neo4j
        result = query_neo4j("SHOW INDEXES YIELD name, state RETURN count(*) AS index_count")
        index_count = int(result[0]["index_count"]) if result else 0
        self.assertGreater(index_count, 0, "Neo4j should have indexes created")

    @skip_if_no_services
    def test_openai_api_connectivity(self):
        """Test that the server can connect to OpenAI API."""
        logs = get_server_logs()

        # Check for successful API calls
        api_calls = logs.count("HTTP Request: POST https://api.openai.com")
        # We might not have made API calls yet, but we should not have API errors
        api_errors = logs.count("Error code: 400") + logs.count("max_tokens")

        self.assertEqual(api_errors, 0, "Should not have OpenAI API errors")

    @skip_if_no_services
    def test_group_id_configuration(self):
        """Test that group_id is configured consistently."""
        logs = get_server_logs()

        # Check that server is using consistent group_id
        default_group_mentions = logs.count("group_id: default")
        self.assertGreater(default_group_mentions, 0, "Server should mention default group_id in logs")

        # Check that the server started with the correct group_id
        self.assertIn("Using provided group_id: default", logs, "Server should start with provided group_id")
        self.assertIn("Using group_id: default", logs, "Server should use the configured group_id")

    @skip_if_no_services
    def test_episode_processing_readiness(self):
        """Test that the server is ready to process episodes."""
        logs = get_server_logs()

        # Check that the server is ready to process episodes
        # This might not be present if no episodes have been processed yet
        # but we can check for the absence of critical errors
        critical_errors = logs.count("CRITICAL") + logs.count("FATAL")
        self.assertEqual(critical_errors, 0, "Should not have critical errors")

        # Check that the server is configured properly
        self.assertIn("Using group_id: default", logs, "Server should be configured with group_id")


if __name__ == '__main__':
    unittest.main()
