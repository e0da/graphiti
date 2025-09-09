#!/bin/bash

# Neo4j Load Script
# Shows dump contents for reference

set -e

# Load shared configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/neo4j-config.sh"

if [ -z "$DUMP_FILE" ]; then
    echo "Error: DUMP_FILE environment variable must be set"
    echo "Available dumps:"
    ls -la $DUMP_DIR/
    exit 1
fi

if [ ! -f "$DUMP_DIR/$DUMP_FILE" ]; then
    echo "Error: Dump file $DUMP_DIR/$DUMP_FILE not found"
    echo "Available dumps:"
    ls -la $DUMP_DIR/
    exit 1
fi

echo "Loading database from dump: $DUMP_FILE"
echo "Note: This shows dump contents. For full restore, use clear_graph MCP tool and rebuild data."
echo "Dump file contents:"
cat $DUMP_DIR/$DUMP_FILE
