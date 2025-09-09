#!/bin/bash

# Neo4j Dump Script
# Creates a dump of the current Neo4j database

set -e

# Load shared configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/neo4j-config.sh"

echo "Creating Neo4j database dump..."

# Ensure dump directory exists
mkdir -p $DUMP_DIR

DUMP_NAME=dump-$(date +%Y%m%d-%H%M%S)
echo "Creating dump: $DUMP_NAME"

# Create the dump file
echo "-- Neo4j Dump created on $(date)" > $DUMP_DIR/$DUMP_NAME.txt
echo "-- All nodes:" >> $DUMP_DIR/$DUMP_NAME.txt
cypher-shell -a bolt://$NEO4J_HOST -u $NEO4J_USER -p $NEO4J_PASSWORD 'MATCH (n) RETURN n' --format plain >> $DUMP_DIR/$DUMP_NAME.txt
echo "-- All relationships:" >> $DUMP_DIR/$DUMP_NAME.txt
cypher-shell -a bolt://$NEO4J_HOST -u $NEO4J_USER -p $NEO4J_PASSWORD 'MATCH ()-[r]->() RETURN r' --format plain >> $DUMP_DIR/$DUMP_NAME.txt

echo "Dump created: $DUMP_NAME.txt"
echo "Available dumps:"
ls -la $DUMP_DIR/
