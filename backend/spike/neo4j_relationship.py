import os
import re
import uuid
from typing import Optional, Dict, Any, List
from neo4j import GraphDatabase, basic_auth
from dotenv import load_dotenv

# --- env 로드 ---
load_dotenv()
URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
USER = os.getenv("NEO4J_USER", "neo4j")
PASSWORD = os.getenv("NEO4J_PASSWORD", "neo4j")

# --- 드라이버 생성 ---
driver = GraphDatabase.driver(URI, auth=basic_auth(USER, PASSWORD))

# (선택) 최초 1회: 유니크 제약
def bootstrap() -> None:
    q = "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Item) REQUIRE n.id IS UNIQUE"
    with driver.session() as s:
        s.execute_write(lambda tx: tx.run(q))

# C: 생성
def create_item(title: str, desc: Optional[str] = None) -> str:
    nid = str(uuid.uuid4())
    q = """
    CREATE (n:Item {id:$id, title:$title, desc:$desc, createdAt:datetime()})
    RETURN n.id AS id
    """
    with driver.session() as s:
        rec = s.execute_write(lambda tx: tx.run(q, id=nid, title=title, desc=desc).single())
        return rec["id"]

# R: 조회
def get_item(item_id: str) -> Optional[Dict[str, Any]]:
    q = "MATCH (n:Item {id:$id}) RETURN n"
    with driver.session() as s:
        rec = s.execute_read(lambda tx: tx.run(q, id=item_id).single())
        return dict(rec["n"]) if rec else None

# U: 수정 (부분 업데이트)
def update_item(item_id: str, *, title: Optional[str] = None, desc: Optional[str] = None) -> bool:
    sets, params = [], {"id": item_id}
    if title is not None:
        sets.append("n.title = $title"); params["title"] = title
    if desc is not None:
        sets.append("n.desc  = $desc");  params["desc"]  = desc
    if not sets:
        return False
    q = f"""
    MATCH (n:Item {{id:$id}})
    SET {", ".join(sets)}, n.updatedAt = datetime()
    RETURN n.id AS id
    """
    with driver.session() as s:
        rec = s.execute_write(lambda tx: tx.run(q, **params).single())
        return rec is not None

# D: 삭제
def delete_item(item_id: str) -> bool:
    q = "MATCH (n:Item {id:$id}) DETACH DELETE n RETURN 1 AS ok"
    with driver.session() as s:
        rec = s.execute_write(lambda tx: tx.run(q, id=item_id).single())
        return rec is not None

# === 관계(relationship) 간단 CRUD ===

# 관계 생성 (기본 타입: RELATES_TO)
def create_relation(from_id: str, to_id: str, kind: str = "RELATES_TO") -> str:
    # 안전: 관계 타입은 대문자/숫자/언더스코어만 허용
    if not re.fullmatch(r"[A-Z][A-Z0-9_]*", kind):
        raise ValueError("Invalid relationship type. Use UPPER_CASE like RELATES_TO or INFLUENCES.")
    q = f"""
    MATCH (a:Item {{id:$from_id}}), (b:Item {{id:$to_id}})
    MERGE (a)-[r:{kind}]->(b)
    ON CREATE SET r.createdAt = datetime()
    RETURN type(r) AS kind
    """
    with driver.session() as s:
        rec = s.execute_write(lambda tx: tx.run(q, from_id=from_id, to_id=to_id).single())
        return rec["kind"]

# 특정 노드의 이웃 관계 조회 (양방향 분리)
def list_relations(item_id: str) -> Dict[str, List[Dict[str, Any]]]:
    q_out = """
    MATCH (a:Item {id:$id})-[r]->(b:Item)
    RETURN type(r) AS kind, b.id AS id, b.title AS title
    ORDER BY kind, title
    """
    q_in = """
    MATCH (a:Item)-[r]->(b:Item {id:$id})
    RETURN type(r) AS kind, a.id AS id, a.title AS title
    ORDER BY kind, title
    """
    with driver.session() as s:
        out_rows = s.execute_read(lambda tx: list(tx.run(q_out, id=item_id)))
        in_rows  = s.execute_read(lambda tx: list(tx.run(q_in,  id=item_id)))
    return {
        "outgoing": [{"kind": r["kind"], "id": r["id"], "title": r["title"]} for r in out_rows],
        "incoming": [{"kind": r["kind"], "id": r["id"], "title": r["title"]} for r in in_rows],
    }

# 관계 삭제
def delete_relation(from_id: str, to_id: str, kind: str = "RELATES_TO") -> int:
    if not re.fullmatch(r"[A-Z][A-Z0-9_]*", kind):
        raise ValueError("Invalid relationship type.")
    q = f"""
    MATCH (a:Item {{id:$from_id}})-[r:{kind}]->(b:Item {{id:$to_id}})
    DELETE r
    RETURN count(*) AS cnt
    """
    with driver.session() as s:
        rec = s.execute_write(lambda tx: tx.run(q, from_id=from_id, to_id=to_id).single())
        return rec["cnt"]

# --- 데모 실행 ---
if __name__ == "__main__":
    try:
        bootstrap()

        # CREATE 노드 2개
        a = create_item("A 아이템", "관계 데모 - 출발")
        b = create_item("B 아이템", "관계 데모 - 도착")
        print("created nodes:", a, b)

        # 관계 생성
        k = create_relation(a, b, "RELATES_TO")
        print("created relation kind:", k)

        # 관계 조회
        print("relations of A:", list_relations(a))

        # 관계 삭제
        removed = delete_relation(a, b, "RELATES_TO")
        print("deleted relations count:", removed)

        # (정리) 노드 삭제
        delete_item(a)
        delete_item(b)

    finally:
        driver.close()
