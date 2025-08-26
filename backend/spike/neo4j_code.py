from typing import Any, Optional, Union
from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j","neo4jneo4j"))

Q_TREE = """
MATCH p = (root:AccountEntry {id:$id})-[:RELATES_TO*1..]->(n:AccountEntry)
WITH collect(p) AS paths
CALL apoc.paths.toJsonTree(paths) YIELD value
RETURN value
"""

def get_tree(root_id: str) -> Optional[Union[dict, list]]:
    with driver.session() as s:
        rec = s.execute_read(lambda tx: tx.run(Q_TREE, id=root_id).single())
        return rec["value"] if rec else None

tree = get_tree("")
print(tree)
