import os
import uuid
from typing import Optional, Dict, Any
from neo4j import GraphDatabase, basic_auth
from dotenv import load_dotenv

# --- env 로드 ---
load_dotenv()
URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
USER = os.getenv("NEO4J_USER", "neo4j")
PASSWORD = os.getenv("NEO4J_PASSWORD", "neo4j")

# --- 드라이버 생성 ---
driver = GraphDatabase.driver(URI, auth=basic_auth(USER, PASSWORD))

def get_start_leaf_items(item_id: str) -> Optional[list[dict]]:
    q = """
    MATCH p = (start:AccountEntry {id:$id})-[*1..]->(leaf:AccountEntry)
    WHERE NOT (leaf)-[]->(:AccountEntry)
    UNWIND nodes(p) AS n
    WITH DISTINCT n
    RETURN collect(n{.*}) AS nodes
    """
    with driver.session() as s:
        rec = s.execute_read(lambda tx: tx.run(q, id=item_id).single())
        if not rec:
            return None
        return rec["nodes"]

if __name__ == '__main__':
    print(get_start_leaf_items(""))
