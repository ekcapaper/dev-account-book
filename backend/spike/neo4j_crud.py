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

if __name__ == "__main__":
    try:
        bootstrap()
        # CREATE
        new_id = create_item("첫 아이템", "env로 연결한 최소 CRUD 데모")
        print("created:", new_id)

        # READ
        print("read:", get_item(new_id))

        # UPDATE
        ok = update_item(new_id, title="제목 수정", desc="설명 수정")
        print("updated:", ok, get_item(new_id))

        # DELETE
        #deleted = delete_item(new_id)
        #print("deleted:", deleted, get_item(new_id))
    finally:
        driver.close()
