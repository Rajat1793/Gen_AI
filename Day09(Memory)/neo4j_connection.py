from neo4j import GraphDatabase

uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "reform-william-center-vibrate-press-5829"))

def test_connection(tx):
    result = tx.run("RETURN 'Neo4j is working!' AS message")
    for record in result:
        print(record["message"])

with driver.session() as session:
    session.read_transaction(test_connection)
