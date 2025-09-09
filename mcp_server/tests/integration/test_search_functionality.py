"""Integration tests for search functionality."""

import unittest
from tests.conftest import query_neo4j, get_server_logs, check_services_running
from tests.test_utils import integration_test, skip_if_no_services


@integration_test
class TestSearchFunctionality(unittest.TestCase):
    """Test search functionality and behavior."""

    @skip_if_no_services
    def test_fulltext_search_on_episodes(self):
        """Test fulltext search on episode content."""
        test_group_id = "search-test"

        # Clean up any existing episodes first
        query_neo4j(
            "MATCH (n:Episodic) WHERE n.group_id = $group_id DELETE n",
            {"group_id": test_group_id}
        )

        # Create test episode
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
                "content": "This episode contains searchable content about healthcare data",
                "group_id": test_group_id
            }
        )

        # Test fulltext search
        search_results = query_neo4j(
            'CALL db.index.fulltext.queryNodes("episode_content", "healthcare data") YIELD node, score RETURN node.name AS name, score ORDER BY score DESC LIMIT 5'
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
    def test_entity_search(self):
        """Test entity search functionality."""
        test_group_id = "entity-search-test"

        # Clean up any existing entities first
        query_neo4j(
            "MATCH (n:Entity) WHERE n.group_id = $group_id DELETE n",
            {"group_id": test_group_id}
        )

        # Create test entity
        query_neo4j(
            """
            CREATE (n:Entity {
                name: $name,
                summary: $summary,
                group_id: $group_id
            })
            """,
            {
                "name": "TestEntity",
                "summary": "A test entity for search functionality testing",
                "group_id": test_group_id
            }
        )

        # Test entity search
        search_results = query_neo4j(
            'CALL db.index.fulltext.queryNodes("node_name_and_summary", "test entity") YIELD node, score RETURN node.name AS name, score ORDER BY score DESC LIMIT 5'
        )

        self.assertGreater(len(search_results), 0, "Entity search should return results")

        # Find our test entity
        test_entity_found = any("TestEntity" in row.get("name", "") for row in search_results)
        self.assertTrue(test_entity_found, "Should find our test entity in search results")

        # Clean up
        query_neo4j(
            "MATCH (n:Entity) WHERE n.group_id = $group_id DELETE n",
            {"group_id": test_group_id}
        )

    @skip_if_no_services
    def test_relationship_search(self):
        """Test relationship search functionality."""
        test_group_id = "relationship-search-test"

        # Clean up any existing data first
        query_neo4j(
            "MATCH (n) WHERE n.group_id = $group_id DETACH DELETE n",
            {"group_id": test_group_id}
        )

        # Create test entities and relationship
        query_neo4j(
            """
            CREATE (a:Entity {name: 'EntityA', group_id: $group_id})
            CREATE (b:Entity {name: 'EntityB', group_id: $group_id})
            CREATE (a)-[r:RELATES_TO {name: $rel_name, fact: $fact, group_id: $group_id}]->(b)
            """,
            {
                "rel_name": "TestRelation",
                "fact": "A test relationship for search functionality testing",
                "group_id": test_group_id
            }
        )

        # Test relationship search
        search_results = query_neo4j(
            'CALL db.index.fulltext.queryRelationships("edge_name_and_fact", "test relationship") YIELD relationship AS rel, score RETURN rel.name AS name, rel.fact AS fact, score ORDER BY score DESC LIMIT 5'
        )

        self.assertGreater(len(search_results), 0, "Relationship search should return results")

        # Find our test relationship
        test_relation_found = any("TestRelation" in row.get("name", "") for row in search_results)
        self.assertTrue(test_relation_found, "Should find our test relationship in search results")

        # Clean up
        query_neo4j(
            "MATCH (n) WHERE n.group_id = $group_id DETACH DELETE n",
            {"group_id": test_group_id}
        )

    @skip_if_no_services
    def test_group_id_filtering_in_search(self):
        """Test that search respects group_id filtering."""
        group_id_1 = "search-group-1"
        group_id_2 = "search-group-2"

        # Clean up any existing data first
        query_neo4j(
            "MATCH (n) WHERE n.group_id IN $group_ids DETACH DELETE n",
            {"group_ids": [group_id_1, group_id_2]}
        )

        # Create episodes in different groups
        query_neo4j(
            """
            CREATE (n:Episodic {
                name: $name,
                content: $content,
                group_id: $group_id,
                source: 'test',
                source_description: 'group filtering test'
            })
            """,
            {
                "name": "Episode Group 1",
                "content": "This episode belongs to group 1",
                "group_id": group_id_1
            }
        )

        query_neo4j(
            """
            CREATE (n:Episodic {
                name: $name,
                content: $content,
                group_id: $group_id,
                source: 'test',
                source_description: 'group filtering test'
            })
            """,
            {
                "name": "Episode Group 2",
                "content": "This episode belongs to group 2",
                "group_id": group_id_2
            }
        )

        # Search for episodes in group 1 only
        group_1_episodes = query_neo4j(
            "MATCH (n:Episodic) WHERE n.group_id = $group_id RETURN n.name AS name, n.group_id AS group_id",
            {"group_id": group_id_1}
        )

        self.assertEqual(len(group_1_episodes), 1, "Should find exactly one episode in group 1")
        self.assertEqual(group_1_episodes[0]["group_id"], group_id_1, "Should be in correct group")
        self.assertEqual(group_1_episodes[0]["name"], "Episode Group 1", "Should be the correct episode")

        # Search for episodes in group 2 only
        group_2_episodes = query_neo4j(
            "MATCH (n:Episodic) WHERE n.group_id = $group_id RETURN n.name AS name, n.group_id AS group_id",
            {"group_id": group_id_2}
        )

        self.assertEqual(len(group_2_episodes), 1, "Should find exactly one episode in group 2")
        self.assertEqual(group_2_episodes[0]["group_id"], group_id_2, "Should be in correct group")
        self.assertEqual(group_2_episodes[0]["name"], "Episode Group 2", "Should be the correct episode")

        # Clean up
        query_neo4j(
            "MATCH (n) WHERE n.group_id IN $group_ids DETACH DELETE n",
            {"group_ids": [group_id_1, group_id_2]}
        )


if __name__ == '__main__':
    unittest.main()
