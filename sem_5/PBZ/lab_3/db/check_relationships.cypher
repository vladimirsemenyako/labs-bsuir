// Check if relationships exist
MATCH ()-[r]->() RETURN type(r) AS relType, count(*) AS count;

// Check OWNS relationships
MATCH (o:Owner)-[:OWNS]->(v:Vehicle) RETURN count(*) AS ownsCount;

// Check HAS_INSPECTION relationships
MATCH (v:Vehicle)-[:HAS_INSPECTION]->(i:Inspection) RETURN count(*) AS inspectionCount;

// Check CONDUCTED relationships
MATCH (e:Employee)-[:CONDUCTED]->(i:Inspection) RETURN count(*) AS conductedCount;

