import os
import uuid
from typing import Any, Dict, List, Optional, Tuple

from neo4j import GraphDatabase, basic_auth
from dotenv import load_dotenv

load_dotenv()

URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
USER = os.getenv("NEO4J_USER", "neo4j")
PASSWORD = os.getenv("NEO4J_PASSWORD", "neo4j")

# ===== 드라이버 =====
driver = GraphDatabase.driver(URI, auth=basic_auth(USER, PASSWORD))


def close_driver():
    driver.close()


# ===== 부트스트랩(유니크 제약 등) =====
def bootstrap() -> None:
    queries = [
        "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Context)  REQUIRE n.id IS UNIQUE",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Decision) REQUIRE n.id IS UNIQUE",
    ]
    with driver.session() as s:
        for q in queries:
            s.execute_write(lambda tx: tx.run(q))


# ===== C(create) =====
def create_context(
    title: str, summary: Optional[str] = None, tags: Optional[List[str]] = None
) -> str:
    nid = str(uuid.uuid4())
    q = """
    CREATE (n:Context {id:$id, title:$title, summary:$summary, tags:$tags, createdAt:datetime()})
    RETURN n.id AS id
    """
    with driver.session() as s:
        rec = s.execute_write(
            lambda tx: tx.run(q, id=nid, title=title, summary=summary, tags=tags or []).single()
        )
        return rec["id"]


def create_decision(
    title: str, summary: Optional[str] = None, tags: Optional[List[str]] = None
) -> str:
    nid = str(uuid.uuid4())
    q = """
    CREATE (n:Decision {id:$id, title:$title, summary:$summary, tags:$tags, createdAt:datetime()})
    RETURN n.id AS id
    """
    with driver.session() as s:
        rec = s.execute_write(
            lambda tx: tx.run(q, id=nid, title=title, summary=summary, tags=tags or []).single()
        )
        return rec["id"]


def create_relation(from_id: str, to_id: str, kind: str = "INFLUENCES") -> str:
    # kind는 화이트리스트로 제한하는 게 안전하지만, 데모라 간단화
    q = f"""
    MATCH (a {{id:$from_id}}), (b {{id:$to_id}})
    MERGE (a)-[r:{kind}]->(b)
    ON CREATE SET r.createdAt = datetime()
    RETURN type(r) AS kind
    """
    with driver.session() as s:
        rec = s.execute_write(lambda tx: tx.run(q, from_id=from_id, to_id=to_id).single())
        return rec["kind"]


# ===== R(read) =====
def get_node(node_id: str) -> Optional[Dict[str, Any]]:
    q = """
    MATCH (n {id:$id})
    RETURN labels(n) AS labels, n AS n
    """
    with driver.session() as s:
        rec = s.execute_read(lambda tx: tx.run(q, id=node_id).single())
        if not rec:
            return None
        data = dict(rec["n"])
        data["labels"] = rec["labels"]
        return data


def list_neighbors(node_id: str) -> List[Dict[str, Any]]:
    q = """
    MATCH (n {id:$id})-[r]->(m)
    RETURN type(r) AS kind, m.id AS id, labels(m) AS labels, m.title AS title
    ORDER BY kind, title
    """
    with driver.session() as s:
        rows = s.execute_read(lambda tx: list(tx.run(q, id=node_id)))
        return [{"kind": r["kind"], "id": r["id"], "labels": r["labels"], "title": r["title"]} for r in rows]


# ===== U(update) =====
def update_node_title(node_id: str, new_title: str) -> bool:
    q = """
    MATCH (n {id:$id})
    SET n.title = $title, n.updatedAt = datetime()
    RETURN n.id AS id
    """
    with driver.session() as s:
        rec = s.execute_write(lambda tx: tx.run(q, id=node_id, title=new_title).single())
        return rec is not None


def upsert_tag(node_id: str, tag: str) -> bool:
    q = """
    MATCH (n {id:$id})
    SET n.tags = apoc.coll.toSet(coalesce(n.tags, []) + $tag), n.updatedAt = datetime()
    RETURN n.id AS id
    """
    with driver.session() as s:
        rec = s.execute_write(lambda tx: tx.run(q, id=node_id, tag=tag).single())
        return rec is not None


# ===== D(delete) =====
def delete_relation(from_id: str, to_id: str, kind: str = "INFLUENCES") -> int:
    q = f"""
    MATCH (a {{id:$from_id}})-[r:{kind}]->(b {{id:$to_id}})
    DELETE r
    RETURN count(*) AS cnt
    """
    with driver.session() as s:
        rec = s.execute_write(lambda tx: tx.run(q, from_id=from_id, to_id=to_id).single())
        return rec["cnt"]


def delete_node(node_id: str) -> int:
    q = """
    MATCH (n {id:$id})
    DETACH DELETE n
    RETURN 1 AS ok
    """
    with driver.session() as s:
        rec = s.execute_write(lambda tx: tx.run(q, id=node_id).single())
        return 1 if rec else 0


# ===== 데모 실행 =====
def demo() -> None:
    bootstrap()
    print("== CREATE ==")
    ctx = create_context("성능 고려", "초기 일정 이슈로 단순화")
    dec = create_decision("싱글스레드+캐시", "락 경쟁 회피, 읽기 캐시")
    rel = create_relation(ctx, dec, "INFLUENCES")
    print("created:", ctx, dec, rel)

    print("\n== READ ==")
    print("context:", get_node(ctx))
    print("neighbors:", list_neighbors(ctx))

    print("\n== UPDATE ==")
    update_node_title(dec, "싱글스레드 + 캐시(개선)")
    upsert_tag(dec, "risk:mid")
    print("updated decision:", get_node(dec))

    print("\n== DELETE ==")
    deleted_rel = delete_relation(ctx, dec, "INFLUENCES")
    print("deleted rel count:", deleted_rel)
    deleted_dec = delete_node(dec)
    deleted_ctx = delete_node(ctx)
    print("deleted nodes:", deleted_dec + deleted_ctx)

    print("\n== DONE ==")


if __name__ == "__main__":
    try:
        demo()
    finally:
        close_driver()
