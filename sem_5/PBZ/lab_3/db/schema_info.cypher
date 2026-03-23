// Database structure visualization queries

// Get all node types and their counts
MATCH (n)
RETURN labels(n) AS nodeType, count(*) AS count
ORDER BY count DESC;

// Get all relationship types and their counts
MATCH ()-[r]->()
RETURN type(r) AS relationshipType, count(*) AS count
ORDER BY count DESC;

// Get full database schema
CALL db.schema.visualization();

// Sample: Get one example of each node type with properties
MATCH (o:Owner)
RETURN o LIMIT 1;

MATCH (v:Vehicle)
RETURN v LIMIT 1;

MATCH (e:Employee)
RETURN e LIMIT 1;

MATCH (i:Inspection)
RETURN i LIMIT 1;

