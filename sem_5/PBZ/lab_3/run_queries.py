from neo4j import GraphDatabase
import sys

URI = "bolt://localhost:7687"
USER = "neo4j"
PASSWORD = "password"

def run_cypher_file(driver, filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    queries = [q.strip() for q in content.split('//') if q.strip() and not q.strip().startswith('//')]
    
    with driver.session() as session:
        for i, query in enumerate(queries, 1):
            if query.strip():
                try:
                    print(f"\n--- Query {i} ---")
                    result = session.run(query)
                    records = list(result)
                    if records:
                        keys = records[0].keys()
                        print(" | ".join(keys))
                        print("-" * 80)
                        for record in records:
                            values = [str(record[key]) for key in keys]
                            print(" | ".join(values))
                    else:
                        print("No results")
                except Exception as e:
                    print(f"Error: {e}")

if __name__ == "__main__":
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
    try:
        if len(sys.argv) > 1:
            filepath = sys.argv[1]
            run_cypher_file(driver, filepath)
        else:
            print("Usage: python run_queries.py <cypher_file>")
    finally:
        driver.close()

