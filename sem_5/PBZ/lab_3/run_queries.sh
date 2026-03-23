#!/bin/bash

NEO4J_URI="bolt://localhost:7687"
NEO4J_USER="neo4j"
NEO4J_PASSWORD="password"

echo "Waiting for Neo4j to be ready..."
sleep 10

echo "Initializing database..."
cypher-shell -a $NEO4J_URI -u $NEO4J_USER -p $NEO4J_PASSWORD < db/init_db.cypher

echo "Running queries..."
cypher-shell -a $NEO4J_URI -u $NEO4J_USER -p $NEO4J_PASSWORD < db/queries.cypher

echo "Done!"

