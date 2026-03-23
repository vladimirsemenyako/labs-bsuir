// Test query to check if data exists
MATCH (n) RETURN labels(n) AS nodeType, count(*) AS count;

// Check owners
MATCH (o:Owner) RETURN o LIMIT 5;

// Check vehicles
MATCH (v:Vehicle) RETURN v LIMIT 5;

// Check relationships
MATCH (o:Owner)-[:OWNS]->(v:Vehicle) RETURN o.fullName, v.licensePlate LIMIT 5;

