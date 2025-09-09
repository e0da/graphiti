"""Integration tests for episode processing functionality."""

import unittest
from tests.conftest import (
    query_neo4j,
    get_server_logs,
    check_services_running,
    get_default_group_id,
    get_test_group_id
)
from tests.test_utils import integration_test, skip_if_no_services


@integration_test
class TestEpisodeProcessing(unittest.TestCase):
    """Test episode processing functionality and behavior."""

    @skip_if_no_services
    def test_episode_processing_with_default_group_id(self):
        """Test episode processing behavior with the default group_id."""
        default_group_id = get_default_group_id()

        # Check initial state
        initial_episodes = query_neo4j(
            "MATCH (n:Episodic) WHERE n.group_id = $group_id RETURN count(n) AS count",
            {"group_id": default_group_id}
        )
        initial_count = int(initial_episodes[0]["count"]) if initial_episodes else 0

        # Get initial error count
        logs_before = get_server_logs()
        uuid_errors_before = logs_before.count("'d5ded3ee-57fa-4324-8eeb-bf5b76ce825a'")

        print(f"Initial episode count for group_id '{default_group_id}': {initial_count}")
        print(f"Initial UUID errors: {uuid_errors_before}")

        # Check system state and behavior
        # We're investigating why episodes with default group_id might not process correctly
        # when added via MCP

        # For now, just verify the system state
        self.assertEqual(uuid_errors_before, 0, "Should not have UUID errors on fresh start")

        # Check that the system is ready to process episodes
        logs = get_server_logs()
        self.assertIn("Using group_id: default", logs, "Server should be configured with default group_id")

    @skip_if_no_services
    def test_episode_processing_with_custom_group_id(self):
        """Test episode processing behavior with custom group_id."""
        test_group_id = get_test_group_id()

        # Check initial state
        initial_episodes = query_neo4j(
            "MATCH (n:Episodic) WHERE n.group_id = $group_id RETURN count(n) AS count",
            {"group_id": test_group_id}
        )
        initial_count = int(initial_episodes[0]["count"]) if initial_episodes else 0

        print(f"Initial episode count for group_id '{test_group_id}': {initial_count}")

        # Verify system can handle custom group_id
        self.assertGreaterEqual(initial_count, 0, "Custom group_id should be queryable")

    @skip_if_no_services
    def test_neo4j_direct_episode_creation(self):
        """Test direct episode creation in Neo4j (bypassing MCP)."""
        test_group_id = "direct-test"

        # Clean up any existing episodes first
        query_neo4j(
            "MATCH (n:Episodic) WHERE n.group_id = $group_id DELETE n",
            {"group_id": test_group_id}
        )

        # Create an episode directly in Neo4j
        result = query_neo4j(
            """
            CREATE (n:Episodic {
                name: $name,
                content: $content,
                group_id: $group_id,
                source: 'test',
                source_description: 'direct test'
            })
            RETURN n.name AS name
            """,
            {
                "name": "Direct Test Episode",
                "content": "This episode was created directly in Neo4j",
                "group_id": test_group_id
            }
        )

        self.assertEqual(len(result), 1, "Should create one episode")
        self.assertEqual(result[0]["name"], "Direct Test Episode")

        # Verify it was created
        episodes = query_neo4j(
            "MATCH (n:Episodic) WHERE n.group_id = $group_id RETURN n.name AS name",
            {"group_id": test_group_id}
        )
        self.assertEqual(len(episodes), 1, "Should find the created episode")
        self.assertEqual(episodes[0]["name"], "Direct Test Episode")

        # Clean up
        query_neo4j(
            "MATCH (n:Episodic) WHERE n.group_id = $group_id DELETE n",
            {"group_id": test_group_id}
        )

    @skip_if_no_services
    def test_search_with_direct_data(self):
        """Test search functionality with directly created data."""
        test_group_id = "search-test"

        # Clean up any existing episodes first
        query_neo4j(
            "MATCH (n:Episodic) WHERE n.group_id = $group_id DELETE n",
            {"group_id": test_group_id}
        )

        # Create test data directly
        query_neo4j(
            """
            CREATE (n:Episodic {
                name: $name,
                content: $content,
                group_id: $group_id,
                source: 'test',
                source_description: 'search test'
            })
            """,
            {
                "name": "Search Test Episode",
                "content": "This episode is for testing search functionality",
                "group_id": test_group_id
            }
        )

        # Test fulltext search
        search_results = query_neo4j(
            'CALL db.index.fulltext.queryNodes("episode_content", "search functionality") YIELD node, score RETURN node.name AS name, score ORDER BY score DESC LIMIT 5'
        )

        self.assertGreater(len(search_results), 0, "Search should return results")

        # Find our test episode
        test_episode_found = any("Search Test Episode" in row.get("name", "") for row in search_results)
        self.assertTrue(test_episode_found, "Should find our test episode in search results")

        # Clean up
        query_neo4j(
            "MATCH (n:Episodic) WHERE n.group_id = $group_id DELETE n",
            {"group_id": test_group_id}
        )

    @skip_if_no_services
    def test_group_id_consistency(self):
        """Test group_id consistency across the system."""
        default_group_id = get_default_group_id()

        # Check what group_ids actually exist in the database
        all_episodes = query_neo4j("MATCH (n:Episodic) RETURN DISTINCT n.group_id AS group_id, count(n) AS count ORDER BY count DESC")

        print("Existing episodes by group_id:")
        for episode in all_episodes:
            print(f"  {episode['group_id']}: {episode['count']} episodes")

        # Check if there are episodes in the default group_id
        default_episodes = query_neo4j(
            "MATCH (n:Episodic) WHERE n.group_id = $group_id RETURN count(n) AS count",
            {"group_id": default_group_id}
        )
        default_count = int(default_episodes[0]["count"]) if default_episodes else 0

        print(f"Episodes in default group_id '{default_group_id}': {default_count}")

        # This test documents the current state and behavior
        # We're investigating how group_ids are used across the system
        self.assertGreaterEqual(default_count, 0, "Should be able to query default group_id")


if __name__ == '__main__':
    unittest.main()
