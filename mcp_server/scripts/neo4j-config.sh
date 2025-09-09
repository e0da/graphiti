#!/bin/bash

# Neo4j Configuration Script
# Shared configuration for Neo4j dump/load operations

# Detect if running in Docker container
if [ -f /.dockerenv ]; then
    NEO4J_HOST="neo4j:7687"
    DUMP_DIR="/dumps"
else
    NEO4J_HOST="localhost:7687"
    DUMP_DIR="./tmp/neo4j-dumps"
fi

# Common Neo4j connection parameters
NEO4J_USER="neo4j"
NEO4J_PASSWORD="neo4j-pw-98723lkjs98723m98uj"
NEO4J_AUTH="$NEO4J_USER:$NEO4J_PASSWORD"
